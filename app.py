from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import File, UploadFile
from estimator.components.predict import Prediction
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
TEMPLATES = Jinja2Templates(directory='templates')
searchedImages = []

predict_pipe = Prediction()


@app.get("/", status_code=200)
@app.post("/")
async def index(request: Request):
    """
    Description : This Route loads the index.html
    """
    return TEMPLATES.TemplateResponse(name='index.html', context={"request": request})


@app.post('/image')
async def upload_file(file: UploadFile = File(...)):
    """
    Description : This Route loads the predictions in a list which will be listed on webpage.
    """
    global searchedImages, predict_pipe
    try:
        if predict_pipe:
            contents = file.file.read() #Once a user upload an image. Read that image
            searchedImages = predict_pipe.run_predictions(contents) #Pass that read image to our pipeline and do the prediction
            return {"message": "Prediction Completed"}
        else:
            return {"message": "First Load Model in Production using reload_prod_model route"}
    except Exception as e:
        return {"message": f"There was an error uploading the file {e}"}


@app.post('/reload')
def reload():
    """
    Description : This Route resets the predictions in a list for reload. Meaning after you have done prediction and can see your output.
    If by any chance you reload your page, you should not be able to see those output again which means you'll have to redo your prediction
    process all over again

    """
    global searchedImages
    searchedImages = []
    return


@app.get('/reload_prod_model')
def reload():
    """
    Description : This Route is Event Triggered or owner controlled to update
                  the model in prod with minimal downtime. So if there is a new model in our bucket, this route will get triggered
    """
    global predict_pipe
    try:
        del predict_pipe #Delete current model in memory
        predict_pipe = Prediction() #After our model in memory is deleted. We can now rerun our pipeline which we implement our new model
        return {"Response": "Successfully Reloaded"}
    except Exception as e:
        return {"Response": e}


@app.get('/gallery')
async def gallery(request: Request):
    """
    Description : This Route lists all the predicted images on the gallery.html listing depends on prediction.
    """
    global searchedImages
    return TEMPLATES.TemplateResponse('gallery.html', context={"request": request, "length": len(searchedImages),
                                                               "searchedImages": searchedImages})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
    #127.0.0.1:8080

