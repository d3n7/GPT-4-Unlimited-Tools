# GPT-4 Unlimited
Custom Plugins for GPT-4 or GPT-3.5-Turbo (easy web app interface)

Current features:
- Googling information
- Computer Vision
- File read/write abilities
- Python script execution

Basically, this app gives GPT-4 access to your command line. (Don't worry! By default you must approve every command manually)

This unlocks the ability for GPT-4 to interact with the internet, APIs, python scripts, and any applications that you could with a CLI. Basically it's open source, flexible, plugins for GPT-4.

Web app: https://huggingface.co/spaces/cbg342/GPT4-Unlimited-Plugins (Windows users are advised to use the HuggingFace)

# Examples

Using BLIP-2 (via Replicate API) to give GPT-4 vision!
<img width="632" alt="robohands" src="https://user-images.githubusercontent.com/29033313/231838517-46e5aecd-09e1-4b65-9b0f-681db64da66f.png">


This information is accurate thanks to it's ability to Google:

<img width="731" alt="Screen Shot 2023-04-09 at 8 08 03 PM" src="https://user-images.githubusercontent.com/29033313/230893716-d08c80a8-267b-412e-9bde-9922aa2c0ef2.png">


Automatic file generation:
<img width="788" alt="Screen Shot 2023-04-08 at 3 55 56 PM" src="https://user-images.githubusercontent.com/29033313/230725162-11ce2407-7375-425c-b6f5-fc994bd5daac.png">
<img width="1313" alt="Screen Shot 2023-04-08 at 3 56 24 PM" src="https://user-images.githubusercontent.com/29033313/230725166-c2815c85-6ee9-43e3-9468-9fe47301b375.png">

<img width="848" alt="Screen Shot 2023-04-08 at 1 07 05 AM" src="https://user-images.githubusercontent.com/29033313/230690667-921ee2d1-6a31-4697-8202-1874bde8c251.png">

Trying to make it self aware lol

<img width="610" alt="Screen Shot 2023-04-10 at 9 44 52 AM" src="https://user-images.githubusercontent.com/29033313/230853393-941784b1-5cba-461c-acc0-3e9cdf208cbe.png">

With a ***fully editable knowledgebase*** to tell GPT-4 what commands it has access to, how they are used, and how they should be run by your CLI.

<img width="1292" alt="Screen Shot 2023-04-07 at 11 59 57 PM" src="https://user-images.githubusercontent.com/29033313/230684178-6511c17a-200d-4af8-ba67-a1fb1cfea9b5.png">

# Installation And Startup
1. ```pip install -r requirements.txt```
2. If using vision plugin, add your Replicate API token to plugins/blip2.py
3. ```streamlit run app.py```

# To Do:
- Better parsing of incorrect command syntax instead of telling GPT to correct itself. (Save tokens)
- Rolling content window to avoid max tokens error
