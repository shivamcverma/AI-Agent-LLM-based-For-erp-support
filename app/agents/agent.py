from openai import OpenAI
import json
import os
from datetime import datetime

def log_unanswered_question(question: str, response: str, reason: str):
    log_file = "logs/unanswered_questions.json"
    os.makedirs("logs", exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "response": response,
        "reason": reason
    }
    
    data = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
            
    data.append(log_entry)
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

from app.utils.text_processor import TextProcessor
from app.config.settings import settings
 
from app.rag.knowledge import KnowledgeBase

from app.tools.student_tools import (
    find_student,
    find_class_id,
    get_student_summary,
    get_student_list
)
from app.tools.fees_tools import (
    get_fees_summary,
    get_student_fee
)

class ERPAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
 
        self.knowledge_base = KnowledgeBase()

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_school_fee_summary",
                    "description": "Get overall school fee collection, total pending fees, and number of students with pending fees.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_student_details",
                    "description": "Fetch details of a student or get the list of all student NAMES in a class/school. Use this whenever the user asks for the names of students in a class or school.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Name of the student to search for (e.g. 'Yash Singh'). Leave empty to get all students in a class."
                            },
                            "class_name": {
                                "type": "string",
                                "description": "Logical name of the class (e.g., 'Class 2', 'Class II', 'Class 10', 'Nursery')."
                            },
                            "gender": {
                                "type": "string",
                                "enum": ["Male", "Female"],
                                "description": "Filter by gender."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_student_fee",
                    "description": "Get fee information (paid, pending, total) for a specific student or an entire class.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Name of the student to lookup fees for (optional if class_name is provided)."
                            },
                            "class_name": {
                                "type": "string",
                                "description": "Class name to get fees for all students in the class, or to narrow down the search (optional)."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_student_summary",
                    "description": "Get a COUNT summary of students (total number of students, how many boys, how many girls). ONLY use this if the user asks 'how many' or 'kitne bache hain'. DO NOT use this if the user asks for their names.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "class_name": {
                                "type": "string",
                                "description": "Class name (e.g., 'Class 2'). Leave empty for whole school."
                            },
                            "gender": {
                                "type": "string",
                                "enum": ["Male", "Female"]
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_classes",
                    "description": "Get a list of classes and sections in the school. Optionally filter by a search string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Optional class name to search for (e.g. 'Class 1', 'Nursery')."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_attendance",
                    "description": "Get attendance for a specific student, or for a whole class, or for the whole school. Use date or from_date/to_date to specify the period.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Student name if looking for a specific student's attendance."
                            },
                            "class_name": {
                                "type": "string",
                                "description": "Class name to get attendance for the whole class, or to help find a specific student."
                            },
                            "date": {
                                "type": "string",
                                "description": "Specific date (YYYY-MM-DD)."
                            },
                            "from_date": {
                                "type": "string",
                                "description": "Start date for a range (YYYY-MM-DD)."
                            },
                            "to_date": {
                                "type": "string",
                                "description": "End date for a range (YYYY-MM-DD)."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_student_marks",
                    "description": "Get the exam results (pass/fail, percentage, grade, rank) for a student.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Student name."
                            },
                            "class_name": {
                                "type": "string",
                                "description": "Optional class name."
                            }
                        },
                        "required": ["search"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_student_subject_marks",
                    "description": "Get detailed subject-wise marks for a student in a specific exam.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Student name."
                            },
                            "class_name": {
                                "type": "string",
                                "description": "Optional class name."
                            },
                            "exam_id": {
                                "type": "integer",
                                "description": "The ID of the exam (you can get this from get_student_marks or get_exams)."
                            }
                        },
                        "required": ["search", "exam_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_staff_summary",
                    "description": "Get staff summary and counts by designation.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_staff_list",
                    "description": "Get the list of all staff members and their designations.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_exams",
                    "description": "Get a list of all exams and their dates for the school.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_teacher_assignments",
                    "description": "Get a list of teachers and which classes/sections they are assigned to.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_erp_guide",
                    "description": "Search the ERP help guide to answer how-to questions about using the software (e.g. 'how to create a class', 'how to add a student').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query (e.g. 'create class' or 'add student')."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    async def execute_tool(self, school_id: int, func_name: str, args: dict):
        class_id = None
        class_name = args.get("class_name")
        if class_name:
            class_id = await find_class_id(school_id, class_name)
            if class_id is None:
                return {"error": f"Class '{class_name}' not found in the ERP."}

        if func_name == "get_school_fee_summary":
            return await get_fees_summary(school_id)

        elif func_name == "get_student_summary":
            gender = args.get("gender")
            if gender and class_id:
                list_res = await get_student_list(school_id, class_id, gender=gender)
                if list_res.get("status") == "success":
                    count = list_res.get("data", {}).get("total", 0)
                    return {"status": "success", "data": {"total_students": count, "gender": gender, "class_name": class_name}}
                return list_res
            
            summary = await get_student_summary(
                school_id=school_id,
                class_id=class_id,
                gender=gender
            )
            if class_id and summary.get("status") == "success":
                male_list = await get_student_list(school_id, class_id, gender="Male")
                female_list = await get_student_list(school_id, class_id, gender="Female")
                male_count = male_list.get("data", {}).get("total", 0) if male_list.get("status") == "success" else 0
                female_count = female_list.get("data", {}).get("total", 0) if female_list.get("status") == "success" else 0
                summary["data"]["boys"] = male_count
                summary["data"]["girls"] = female_count
            
            return summary

        elif func_name == "get_student_details":
            search = args.get("search")
            if search:
                result = await find_student(school_id, search)
                if result.get("status") == "not_found":
                    return result
                
                students = []
                if result.get("status") == "success":
                    students = [result["student"]]
                elif result.get("status") == "multiple":
                    students = result["students"]
                
                if class_id:
                    students = [s for s in students if s.get("class_id") == class_id]
                
                if not students:
                    return {"status": "not_found", "message": f"Student '{search}' not found in class '{class_name}'."}
                
                if len(students) == 1:
                    return {"status": "success", "student": students[0]}
                else:
                    return {"status": "multiple", "students": students}
            else:
                result = await get_student_list(
                    school_id=school_id,
                    class_id=class_id,
                    gender=args.get("gender")
                )
                return result

        elif func_name == "get_student_fee":
            search = args.get("search")
            if not search and not class_id:
                return {"error": "Please provide a student name or a class name."}
            
            async def get_fees_for_students(students_list):
                results = []
                for s in students_list:
                    fee_res = await get_student_fee(school_id, s["id"])
                    results.append({"student": s, "fee": fee_res})
                return results

            if search:
                result = await find_student(school_id, search)
                if result.get("status") == "not_found":
                    return {"error": f"No student named '{search}' found."}
                    
                students = []
                if result.get("status") == "success":
                    students = [result["student"]]
                elif result.get("status") == "multiple":
                    students = result["students"]
                
                if class_id:
                    students = [s for s in students if s.get("class_id") == class_id]
                
                if not students:
                    return {"error": f"No student named '{search}' found in class '{class_name}'."}
                
                return await get_fees_for_students(students)
            else:
                result = await get_student_list(school_id, class_id=class_id)
                if result.get("status") == "success":
                    students = result.get("data", {}).get("students", [])
                    return await get_fees_for_students(students)
                return {"error": "Could not fetch students for the class."}

        elif func_name == "get_classes":
            search = args.get("search")
            if search:
                from app.tools.classes import search_classes
                return await search_classes(school_id, search)
            else:
                from app.tools.classes import get_classes
                return await get_classes(school_id)

        elif func_name == "get_attendance":
            from app.tools.attendance_tools import get_attendance_summary
            search = args.get("search")
            date = args.get("date")
            from_date = args.get("from_date")
            to_date = args.get("to_date")
            
            if search:
                result = await find_student(school_id, search)
                if result.get("status") == "not_found":
                    return {"error": f"No student named '{search}' found."}
                
                students = [result["student"]] if result.get("status") == "success" else result["students"]
                if class_id:
                    students = [s for s in students if s.get("class_id") == class_id]
                if not students:
                    return {"error": f"No student named '{search}' found in class '{class_name}'."}
                
                results = []
                for s in students:
                    att = await get_attendance_summary(school_id, date=date, student_id=s["id"], from_date=from_date, to_date=to_date)
                    results.append({"student": s, "attendance": att})
                return results
            else:
                return await get_attendance_summary(school_id, date=date, class_id=class_id, from_date=from_date, to_date=to_date)

        elif func_name == "get_student_marks":
            from app.tools.marks_tools import get_student_marks
            search = args.get("search")
            result = await find_student(school_id, search)
            if result.get("status") == "not_found":
                return {"error": f"No student named '{search}' found."}
            
            students = [result["student"]] if result.get("status") == "success" else result["students"]
            if class_id:
                students = [s for s in students if s.get("class_id") == class_id]
            if not students:
                return {"error": f"No student named '{search}' found in class '{class_name}'."}
            
            results = []
            for s in students:
                marks = await get_student_marks(school_id, s["id"])
                results.append({"student": s, "marks": marks})
            return results

        elif func_name == "get_student_subject_marks":
            from app.tools.marks_tools import get_student_subject_marks
            search = args.get("search")
            exam_id = args.get("exam_id")
            result = await find_student(school_id, search)
            if result.get("status") == "not_found":
                return {"error": f"No student named '{search}' found."}
            
            students = [result["student"]] if result.get("status") == "success" else result["students"]
            if class_id:
                students = [s for s in students if s.get("class_id") == class_id]
            if not students:
                return {"error": f"No student named '{search}' found in class '{class_name}'."}
            
            results = []
            for s in students:
                marks = await get_student_subject_marks(school_id, s["id"], exam_id)
                results.append({"student": s, "subject_marks": marks})
            return results

        elif func_name == "get_staff_summary":
            from app.tools.staff_tools import get_staff_summary
            return await get_staff_summary(school_id)

        elif func_name == "get_staff_list":
            from app.tools.staff_tools import get_staff_list
            return await get_staff_list(school_id)

        elif func_name == "get_exams":
            from app.tools.exam_tools import get_exams
            return await get_exams(school_id)

        elif func_name == "get_teacher_assignments":
            from app.tools.teacher_assignments import get_teacher_assignments
            return await get_teacher_assignments(school_id)

        elif func_name == "search_erp_guide":
            query = args.get("query", "")
            results = self.knowledge_base.search(query, top_k=3)
            if not results:
                return {"message": "No help guide found for this query."}
            
            # Format the output for the LLM
            return {
                "results": [
                    {
                        "intent": r.get("intent", ""),
                        "steps": r.get("answer", "")
                    }
                    for r in results
                ]
            }

    async def process(self, message: str, school_id: int, conversation_history: list[dict] | None = None, previous_understanding: dict | None = None):
        print(f"\n\n{'='*50}\n[USER QUESTION]: {message}\n{'='*50}\n")
        conversation_history = conversation_history or []
        
        system_prompt = """You are a highly intelligent and helpful School ERP Assistant.
Your primary role is to answer user queries accurately by calling the appropriate ERP tools.
Rules:
1. Always use tools to fetch data. Never guess student details or fee amounts.
2. The user might ask follow-up questions. Use your conversational memory to infer context (like which class or student they are talking about).
3. If a tool returns multiple students (e.g. 2 students named "Yash Singh"), you can provide details for all of them! Do not simply ask for the class if you can just print their details.
4. If a tool returns an error or says "not found", politely inform the user.
5. Provide your final answer in conversational Hindi (written in English script), Hinglish, or English as appropriate to the user's language. Keep answers natural, polite, and to the point.
6. If the user asks about fees, state amounts clearly (e.g. '₹5000').
7. DO NOT use markdown formatting like bold (**text**) or italics (*text*) in your response. Keep it completely plain text without any stars (*).
8. Differentiate between students and teachers based on context. If a user asks which class a person is "assigned" to (e.g. "X ko kon si class assign hai"), they mean a teacher, so use get_teacher_assignments."""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history[-10:]:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": message})

        print("CALLING LLM WITH TOOLS...")
        response = self.client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=self.get_tools(),
            tool_choice="auto",
            temperature=0.3
        )

        message_obj = response.choices[0].message
        
        if message_obj.tool_calls:
            # Add assistant message with tool calls to history
            assistant_message = {
                "role": "assistant",
                "content": message_obj.content,
                "tool_calls": [
                    {
                        "id": t.id,
                        "type": "function",
                        "function": {
                            "name": t.function.name,
                            "arguments": t.function.arguments
                        }
                    } for t in message_obj.tool_calls
                ]
            }
            messages.append(assistant_message)
            
            # Execute tools
            with open("debug_log.txt", "a") as f:
                f.write(f"\n\n--- NEW REQUEST ---\n")
            
            tool_results_list = []
            for tool_call in message_obj.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"EXECUTING TOOL: {func_name} with args {args}")
                
                try:
                    result_json = await self.execute_tool(school_id, func_name, args)
                except Exception as e:
                    result_json = {"error": str(e)}
                
                tool_results_list.append(result_json)
                
                print(f"TOOL RESULT ({func_name}):", result_json)
                with open("debug_log.txt", "a") as f:
                    f.write(f"TOOL: {func_name}\nARGS: {args}\nRESULT: {json.dumps(result_json)}\n")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result_json, default=str)
                })
            
            print("CALLING LLM FOR FINAL RESPONSE...")
            messages.append({
                "role": "system",
                "content": "You have all the required information. Do not output any <tool_call> tags. Provide the final answer in natural language to the user."
            })
            final_response = self.client.chat.completions.create(
                model="openrouter/free",
                messages=messages,
                temperature=0.3
            )
            final_content = final_response.choices[0].message.content or ""
            
            final_content = final_content.replace('*', '')
            
            print(f"\n{'='*50}\n[LLM RESPONSE]:\n{final_content}\n{'='*50}\n")
            
            # Check for errors in tool results to log unanswered queries
            has_error = False
            for r in tool_results_list:
                if isinstance(r, dict):
                    if "error" in r or r.get("status") == "not_found" or "message" in r:
                        has_error = True
                elif isinstance(r, list):
                    for item in r:
                        if isinstance(item, dict) and ("error" in item or item.get("status") == "not_found"):
                            has_error = True
            
            # Also check if the LLM explicitly stated it couldn't find the answer
            lower_content = final_content.lower()
            failure_keywords = [
                "maaf kijiye", 
                "nahi mil raha", 
                "nahi mila", 
                "nahi mil rahe",
                "nahi mil rahi",
                "not found", 
                "unable to find"
            ]
            if not has_error:
                for kw in failure_keywords:
                    if kw in lower_content:
                        has_error = True
                        break
            
            if has_error:
                log_unanswered_question(message, final_content, "Tool returned error or LLM could not find answer")
            
            return {
                "success": True,
                "intent": "llm_agent",
                "response": final_content,
                "data": []
            }
        else:
            final_content = message_obj.content or ""
            final_content = final_content.replace('*', '')
            print(f"\n{'='*50}\n[LLM RESPONSE]:\n{final_content}\n{'='*50}\n")
            
            # If no tools were called, it might be an unanswerable query (or general chat)
            log_unanswered_question(message, final_content, "No tool was called by LLM")
            
            return {
                "success": True,
                "intent": "llm_agent",
                "response": final_content,
                "data": []
            }