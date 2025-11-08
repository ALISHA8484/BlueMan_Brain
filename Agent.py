import sys
from config import liara_chat_client
from RAG import query_vector_store, get_embedding_model

def route(question: str):
    """
    سوال کاربر را به 'DOCUMENT' یا 'GENERAL' دسته‌بندی می‌کند.
    """
    system_prompt = """
        You are a routing-assistant. Your job is to classify the user's question 
        into one of two categories: 'DOCUMENT' or 'GENERAL'.

        The 'DOCUMENT' category is for any question about [مسابقات رباتیک دانشگاه صنعتی اصفهان ,RoboIUT,قوانین مسابقات , لیگ چالش صنعتی
        و لیگ مسیریابو لیگ حل ماز و چالش صنعتی مقدماتی و پیشرفته, جوایز هر لیگ,محل برگزاری این مسابقات و تاریخ برگزاری].
        The 'GENERAL' category is for all other questions (e.g., greetings, weather, facts, spetialized questions that are not provided in the document).

        Respond with *only* the single word 'DOCUMENT' or 'GENERAL'.
    """
    print(f"Routing question: '{question}'")
    try:
        completion = liara_chat_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,  # برای دسته‌بندی، دما را صفر می‌گذاریم
            max_tokens=5    # فقط یک کلمه نیاز داریم
        )
        response_content = completion.choices[0].message.content.strip()
        print(f"Route determined: {response_content}")


        if response_content in ["DOCUMENT", "GENERAL"]:
            return response_content
        else:
            print(f"Routing error: Unexpected response '{response_content}'. Defaulting to GENERAL.")
            return "GENERAL"

    except Exception as e:
        print(f"An error occurred during the routing API call: {e}")
        return "GENERAL"

def generate_rag_answer(question: str, context: str):

    print("Generating answer based on RAG context...")
    
    rag_system_prompt = """
    شما یک دستیار متخصص در مورد "مسابقات رباتیک IUT-RC 1404" هستید.
    وظیفه شما این است که به سوال کاربر، *با استفاده از* "متن مرجع" (Context) که در ادامه می‌آید، پاسخ دهید.
    - پاسخ شما باید کاملاً بر اساس متن مرجع باشد.
    - اگر پاسخ سوال در متن مرجع وجود ندارد، به وضوح بگویید: "متاسفانه اطلاعاتی در این مورد در اسناد من وجود ندارد."
    - پاسخ تو باید بر اساس متن مرجع تهیه شده باشد و میتوانی از اطلاعات عمومی ات برای اضافه کردن اطلاعات استفاده کنی
    - پاسخ را به زبان فارسی و به صورت روان ارائه دهید.
    -پاسخ حدود 30 کلمه بیشتر نباشد
    """
    
    user_prompt = f"""
    متن مرجع (Context):
    ---
    {context}
    ---
    
    سوال کاربر:
    {question}
    
    پاسخ:
    """
    
    try:
        completion = liara_chat_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": rag_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        response_content = completion.choices[0].message.content
        return response_content
    except Exception as e:
        print(f"An error occurred during the RAG answer generation: {e}")
        return "متاسفانه در هنگام پردازش پاسخ خطایی رخ داد."

def generate_general_answer(question: str):

    print("Generating general answer...")
    
    general_system_prompt = "شما یک دستیار هوش مصنوعی عمومی و مفید هستید. به سوال کاربر به بهترین شکل و به زبان فارسی پاسخ دهید."
    
    try:
        completion = liara_chat_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": general_system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )
        response_content = completion.choices[0].message.content
        return response_content
    except Exception as e:
        print(f"An error occurred during the general answer generation: {e}")
        return "متاسفانه در هنگام پردازش پاسخ خطایی رخ داد."