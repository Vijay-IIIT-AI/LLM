
Function:

run_translation(mode, source, output=None, target_lang="Korean", max_slides=None)

[1] mode → what type of input ("pptx", "file", or "text")
[2] source → the thing to translate (file path or text string)
[3] output → where to save result (pptx/txt file path). Optional for text mode
[4] target_lang → language to translate into (default: Korean)
[5] max_slides → limit number of slides to translate in PPTX (default: all)

Postive Case:
-------------

Type 1:( When user Give only text)

Input:
run_translation("text", "What are you doing?", target_lang="Korean")

Output Expected:
{'status': 'completed', 'message': None, 'translated_content': '무엇을 하고 계세요?'}

Type 2: (When  User Give Pptx file) (ppt file is not supported on pptx is supported)
------------

Input:
run_translation("pptx", r"/content/Final_Review_PPT_2.pptx", "output_ko.pptx", target_lang="Korean"))

Output Expected:
{'status': 'completed', 'message': None, 'translated_content': 'output_ko.pptx'}


Type 3: (When User Uploads a txt File) 
---------------------------------

Input:
print(run_translation("file", r"/content/sample.txt", "/content/output_ta.txt", target_lang="Korean"))


Output Expected:
{'status': 'completed', 'message': None, 'translated_content': '/content/output_ta.txt'}


Negative Case:
--------------

{'status': 'failed', 'message': "[Errno 2] No such file or directory: '/content/sampe.txt'", 'translated_content': None}

{'status': 'failed', 'message': "Package not found at '/content/MachineLearning.ppt'", 'translated_content': None}
