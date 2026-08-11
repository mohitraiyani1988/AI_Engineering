response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain what an API is in one paragraph."
)

print(response)


sdk_http_response=HttpResponse(
  headers=<dict len=12>
) candidates=[Candidate(
  content=Content(
    parts=[
      Part(
        text='An **API**, or **Application Programming Interface**, acts as a digital messenger that allows different software applications to communicate and share data with one another. Think of it like a waiter in a restaurant: you (the user) choose what you want from the menu, the waiter (the API) takes your request to the kitchen (the server), and then delivers the food (the data) back to your table. By defining a standard set of rules and protocols, APIs enable developers to seamlessly integrate external services—such as displaying Google Maps inside a ride-sharing app or processing payments via PayPal—without having to write that complex functionality from scratch.',
        thought_signature=b'\x12\x85\x0e\n\x82\x0e\x01\x11M2\x0f\xe0\x006Q\xb12\x8bz\xb3\x87\xb6\xdfvy\x88\x95j\xe5\x0f\xe2\xc2\x007\xd7\xbb`\xfed\x94zg\x9d\x1eO\x9b\x0f\xfaK\xd9\xca8\x02{i\x17\x1e[m31{6N/\xa9B\xff\x15\xf0\xa52\x15\x0clT\xc7\x89\x8c\x1d\x19\xd1\x1cV}\x83e\xd9E\x8b\xbf\x92\xd0\x1c\x15\x84\xf2...'
      ),
    ],
    role='model'
  ),
  finish_reason=<FinishReason.STOP: 'STOP'>,
  index=0
)] create_time=None model_version='gemini-3.5-flash' prompt_feedback=None response_id='JlB7aq2mOriQjuMP7tSEkQQ' usage_metadata=GenerateContentResponseUsageMetadata(
  candidates_token_count=128,
  prompt_token_count=10,
  prompt_tokens_details=[
    ModalityTokenCount(
      modality=<MediaModality.TEXT: 'TEXT'>,
      token_count=10
    ),
  ],
  thoughts_token_count=383,
  total_token_count=521
) model_status=None automatic_function_calling_history=[] parsed=None


### contents="Explain what an API is in 2 lines."

sdk_http_response=HttpResponse(
  headers=<dict len=12>
) candidates=[Candidate(
  content=Content(
    parts=[
      Part(
        text="""An API (Application Programming Interface) is a software intermediary that allows two different applications to communicate and share data with each other. 
It acts like a digital messenger, delivering your request to a system and bringing the response back to your screen.""",
        thought_signature=b"\x12\x83\x10\n\x80\x10\x01\x11M2\x0fX\xd0u\xf8\xd23K\xc2N\xf0\xb9F\x19\x05T\xa3]S?\xcfW\xa3\xaf\x13<\x90\xe1\xd9\xe6l&Y\x1d\xb9\xf3h\x9f\xff)\x18n\xa4\xe0G^\xe6rf\x06B\xef\n\xd2\x87\xe7l\x8f\x19A\xf7]?f\x06\xa3\x85i(O\xbaA\x89\x81\xc5\x8f\xaa>!\\\xb5\r\xdb0'\x82Q...'
      ),
    ],
    role='model'
  ),
  finish_reason=<FinishReason.STOP: 'STOP'>,
  index=0
)] create_time=None model_version='gemini-3.5-flash' prompt_feedback=None response_id='V1F7ao2MEoSMjuMPp_uLiQU' usage_metadata=GenerateContentResponseUsageMetadata(
  candidates_token_count=49,
  prompt_token_count=11,
  prompt_tokens_details=[
    ModalityTokenCount(
      modality=<MediaModality.TEXT: 'TEXT'>,
      token_count=11
    ),
  ],
  thoughts_token_count=470,
  total_token_count=530
) model_status=None automatic_function_calling_history=[] parsed=None

### contents="Explain what an API is."
sdk_http_response=HttpResponse(
  headers=<dict len=12>
) candidates=[Candidate(
  content=Content(
    parts=[
      Part(
        text="""At its simplest, an **API** (which stands for **Application Programming Interface**) is a software intermediary that allows two different applications to talk to each other. 

Think of it as a **messenger** that takes a request from you, tells a system what you want to do, and then brings the response back to you.

---

### The Restaurant Analogy

The easiest way to understand an API is to imagine you are dining at a restaurant:

1. **You (The User/Client):** You are sitting at the table looking at the menu. You know what you want to order.
2. **The Kitchen (The Server/Database):** This is the system that prepares your food. It has all the ingredients and resources, but you can’t go directly into the kitchen to get your food.
3. **The Waiter (The API):** This is the crucial link. The waiter takes your order (your request), delivers it to the kitchen, and then brings the food (the response) back to your table. 

Without the waiter (the API), you wouldn't be able to get your food from the kitchen.

---

### Real-World Examples of APIs

You use APIs every day without even realizing it. Here are a few common examples:

* **Weather Apps:** When you look at the weather app on your phone, the phone company doesn't have its own weather satellites. Instead, the app uses an API to "ask" a weather service (like Weather.com) for the current forecast and displays it on your screen.
* **Pay with PayPal:** When you buy something online, the retail website doesn't access your bank account directly. Instead, it uses PayPal's API to send the purchase amount, PayPal processes the payment securely, and the API sends a message back saying, "Payment successful!"
* **Log In with Google/Facebook:** When a website asks you to log in using your Facebook or Google account, it uses an API to verify your identity with Facebook/Google without actually giving the website your password.
* **Uber:** Uber’s app doesn't build its own mapping software. Instead, it uses the **Google Maps API** to display maps and calculate routes.

---

### Why are APIs so important?

1. **They save time:** Developers don’t have to reinvent the wheel. If a developer wants to add a map to their app, they don't have to build a global mapping system; they just plug in the Google Maps API.
2. **They provide security:** APIs act as a gatekeeper. When your phone talks to a server via an API, it only shares the specific data needed for that transaction, keeping the rest of your phone’s data (and the server's database) safe.
3. **They allow automation:** Instead of a human manually moving data from one program to another, APIs allow software programs to share data instantly and automatically.

### Summary
An API is a **digital bridge** that allows different software programs to share data and functionalities securely and efficiently.""",
        thought_signature=b'\x12\xd4\x17\n\xd1\x17\x01\x11M2\x0f_\x16Ck*\x87\x15/\xfe>P\x1bK\xe5[\xae\xea\xd0\xbc\xaf\xbe-Ft\xe0\xb0\xb3~\xd7\n\xe7L\xd2\x81-K\xf9\xf0\xda\xd0\xeb\xebz\xdb\'j\xd8vz\xe4r\xad\n\xf4\x06\xa2\xb5\xe1\xdf"\xd8\x7f\xbfaIN\x8f\x97\xc3\x1f\xf0/\x15a\x9er\x9aF[@\xb9_\x15*s\xcc...'
      ),
    ],
    role='model'
  ),
  finish_reason=<FinishReason.STOP: 'STOP'>,
  index=0
)] create_time=None model_version='gemini-3.5-flash' prompt_feedback=None response_id='x1F7avuoJ_jEg8UPrrqMmQM' usage_metadata=GenerateContentResponseUsageMetadata(
  candidates_token_count=640,
  prompt_token_count=7,
  prompt_tokens_details=[
    ModalityTokenCount(
      modality=<MediaModality.TEXT: 'TEXT'>,
      token_count=7
    ),
  ],
  thoughts_token_count=770,
  total_token_count=1417
) model_status=None automatic_function_calling_history=[] parsed=None

### contents="Explain what is API in short."

sdk_http_response=HttpResponse(
  headers=<dict len=12>
) candidates=[Candidate(
  content=Content(
    parts=[
      Part(
        text="""An **API (Application Programming Interface)** is a software intermediary that allows two different applications to talk to each other. 

Think of it as a **waiter** in a restaurant:
1. **You (the customer)** sit at the table and look at the menu (the app).
2. **The waiter (the API)** takes your order (your request) and delivers it to the **kitchen (the server/database)**.
3. The kitchen prepares the food and gives it to the waiter, who brings the response **(your food)** back to you.

**Real-world example:** When you book a flight on a travel site (like Expedia), the site uses APIs to instantly request ticket prices from various airline databases and show them all to you in one place.""",
        thought_signature=b'\x12\xcb\r\n\xc8\r\x01\x11M2\x0f\x94,\xd1}a\xad7;Y\xf5\xab/\xad\xbd \xc1\x90oU\x01Kw>&c\xd4\x812$\x1a\xab\xb3\x1c\x8cxV\xb7iM\xb5\xc9\x11w\xf6@\xab\x88;E3\xe1\x14\xe1B\x9biP\xee\x9f\xb3\xc7I\xbe\xd6w\x02\xa8\xa7srr\x10\xa9\xe7!\xae\xd4)6?G]\xa1\xa6B\x8b...'
      ),
    ],
    role='model'
  ),
  finish_reason=<FinishReason.STOP: 'STOP'>,
  index=0
)] create_time=None model_version='gemini-3.5-flash' prompt_feedback=None response_id='NFJ7aquGIMvZjuMPt7v5wAQ' usage_metadata=GenerateContentResponseUsageMetadata(
  candidates_token_count=162,
  prompt_token_count=8,
  prompt_tokens_details=[
    ModalityTokenCount(
      modality=<MediaModality.TEXT: 'TEXT'>,
      token_count=8
    ),
  ],
  thoughts_token_count=409,
  total_token_count=579
) model_status=None automatic_function_calling_history=[] parsed=None