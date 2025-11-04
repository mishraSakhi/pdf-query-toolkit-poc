from pyngrok import ngrok

# Start tunnel on port 8000
public_url = ngrok.connect(8000)
print("Public URL:", public_url)

# Now you can run uvicorn as usual
# uvicorn main:app --reload
