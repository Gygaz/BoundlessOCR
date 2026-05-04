import shutil
import gc
import os
import img2pdf
from pypdf import PdfReader, PdfWriter
from ocr.splitter import pdfSplitter
from ocr.upscaler import Upscaler
from ocr.scanner import Scanner
from PySide6.QtCore import QThread, Signal, Slot
from PIL import Image

class Worker(QThread):
    status_message = Signal(str)
    finished = Signal()
    progress_update = Signal(int)   
    
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    tempPath= os.path.join(dir_path, "extracted_temp") 
    upscale_folder= os.path.join(dir_path, "upscaled_pages")
    pdf_Folder= os.path.join(dir_path, "processed_pdfs")
    txt_folder= os.path.join(dir_path, "txt_files")

    def __init__(self):
        super().__init__()
    
    def clean_temp_files(self):
        #shutil.rmtree(self.upscale_folder)
        #shutil.rmtree(self.tempPath)
        upscaler= None

    def create_paths(self):
        os.makedirs(self.tempPath, exist_ok=True)        
        os.makedirs(self.upscale_folder, exist_ok=True)        
        os.makedirs(self.pdf_Folder, exist_ok=True)            
        os.makedirs(self.txt_folder, exist_ok=True)

    def process_pdf(self, source, ui_element):
        self.create_paths()     
        self.status_message.emit("Disassembling pdf")

        reader = PdfReader(source[0])
        pages = len(reader.pages)

        if pages > 50:
            splitPath = os.path.join(self.dir_path, "splitPdfs", os.path.splitext(os.path.basename(source[0]))[0]).replace(" ", "_")
            os.makedirs(splitPath, exist_ok=True)
            self.status_message.emit("Splitting large pdfFileinto smaller subfiles")
            newSource = pdfSplitter.fragment_pdf(source[0], pages, splitPath)
            source = newSource

        self.status_message.emit(f"Document was split into {len(source)} parts")
        
        RealESRGAN= os.path.join(self.dir_path, "model", "RealESRGAN_x4plus_anime_6B.pth")
        upscaler= None

        for index, pdfFile in enumerate(source):
            self.status_message.emit(f"Processing part {index +1}")
            imageList= pdfSplitter.convert_pdf_to_png(pdfFile, self.tempPath)

            if index ==0:
                with Image.open(imageList[0]) as img:
                    width, _ = img.size
                    ratio =  round(1540/width)
                    if ratio<4 and ratio!=1:
                        ratio=4
             
            processedList= []
            processed_pdf= os.path.join(self.pdf_Folder ,f"upscaled_{os.path.basename(pdfFile)}")

            for index, image_path in enumerate(imageList):
                if ratio > 1:
                    Upscaler.set_scale(ratio)
                    upscaler = Upscaler.setup_upscaler(RealESRGAN)
                    self.status_message.emit(f"Upscaling page {index +1}")
                    print("Upscaling")
                    file_name= os.path.basename(image_Path)
                    image_path= os.path.join(self.upscale_folder, f"upscaled_{file_name}")
                    if os.path.exists(image_path) is False:
                        Upscaler.process_image(upscaler, image_Path, image_path, 2048)
                processedList.append(image_path)
            
            upscaler=None

            if False:
                if processedList:
                    self.status_message.emit(f"Saving upscaled PDF at {processed_pdf}")
                    with open(processed_pdf, "wb") as f:
                        f.write(img2pdf.convert(processedList))

            self.status_message.emit(f"Successfully scaled : {os.path.basename(pdfFile)} {ratio}X")
            gc.collect()

            base=os.path.basename(pdfFile)       
            folder_name= os.path.splitext(base)[0]                          
            os.makedirs(os.path.join(self.txt_folder, folder_name), exist_ok=True)

            for page, image_path in enumerate(processedList):                
                txt_path= os.path.join(self.txt_folder, folder_name, f"{folder_name}_{page+1}.txt")
                if os.path.exists(txt_path):
                    self.status_message.emit(f'{os.path.basename(txt_path)} already exists, skipping')
                    self.progress_update.emit(page+1)
                    continue
                self.status_message.emit(f"Scanning page {page+1}")
                print(f"Scanning page {page+1}")
                ocr = Scanner()
                text= ocr.scan(image_path)   
                with open(txt_path, "w") as file:
                    file.write(text)
                self.status_message.emit(f"Wrote {txt_path}")
            self.status_message.emit(f"Saved txt files at {folder_name}")

        self.clean_temp_files()