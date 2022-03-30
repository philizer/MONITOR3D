import multiprocessing
import threading
import shutil
from fastapi import FastAPI, UploadFile, File
from serial_comm import PrinterManager, PrinterCommand
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()


class Command(BaseModel):
    command:str

#safer:
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],  # not safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pos = multiprocessing.Array("d", 3)
p1 = PrinterManager()
#s = p1.openConnection()
t1 = threading.Thread(target=p1.manage_printer_thread_target, args=(
    pos,), daemon=True) 
t1.start()



@app.post("/cmd") 
async def uploadCmdQueue(data:Command):
    cmde=data.command
    p1.qCmd.put(PrinterCommand(cmde))
    print(cmde)
    return {f"{cmde}": " Added To Queue Success"}



@app.get("/advancement")
async def currentAdvancement():
    if p1.printing:
        dic = {"progress": round(
            ((p1.currentPrintTotSize-p1.qFile.qsize())/p1.currentPrintTotSize)*100)}
    else:
        dic = {"progress": "Not printing"}
    return dic


@app.get("/position")
async def currentPosition():
    return {"x": pos[0], "y": pos[1], "z": pos[2]}


@app.post("/uploadGcode")
async def uploadGcode(file: UploadFile = File(...)):
    if(".gcode" in file.filename):
        with open(f'{file.filename}', "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        p1.fillQueueGcodeFile(file.filename)
        p1.current_print = file.filename
        p1.paused = False
        return "Print will start after heating"
    else:
        pass #or raise exception
