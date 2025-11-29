# warsaw-ai-hackaton

~ ❯ curl -X POST http://localhost:8899/segment_image   -F 'chat_history={
    "messages":[
      {"role":"user","content":"Hi, I would like you to analyse an image for me."},
      {"role":"assistant","content":"Sure, please upload the image you want me to analyse."},
      {"role":"user","content":"Please count the trucks visible on the field in this image."}
    ]
  }'   -F "image=@bigg.jpg"
{"chat_response":"Na zdjęciu widoczne są 5 ciężarówek.","masked_image_path":"Images/masked_upload_bigg.png"}

# jak uruchomić backend
 
w `src/` `./run_backend.sh` i trzymać mocno kciuki, że będzie działać 