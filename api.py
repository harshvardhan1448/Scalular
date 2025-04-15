from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse,HTMLResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pymupdf
import google.generativeai as genai
import json
import base64 
import os
import fitz
import pandas as pd
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import io

load_dotenv()



class quotation_response(BaseModel):
    gender: str
    quantity_in_gms: int
    product_name: str
    category: str
    zipper:bool
    logo_embroidery:bool
    size:str

class products(BaseModel):
    product:list[quotation_response]

class fabric(BaseModel):
    fabric_and_blend:str
    print:str

templates = Jinja2Templates(directory="templates")

obj=json.load(open("object.json",'r'))

app=FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")
api_key=os.environ['api_key']
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
print("HI")

@app.get("/",response_class=JSONResponse)
@app.get("/alive",response_class=JSONResponse)
async def alive():
    print("Healthy")
    return JSONResponse(content={"status":"Healthy"},status_code=200)

class File_request:
    def __init__(self,request:Request):
        self.request: Request=request
    
    async def load_data(self):
        form= await self.request.form()
        self.upload_file = form.get("file").file.read()

async def extract_info(base64_image):
    image_data = base64.b64decode(base64_image)
    
    # Create generation config for structured output
    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
    }
    
    prompt = """Analyze this image and extract the following information in JSON format:
    {
        "gender": "men/women/kids",
        "quantity_in_gms": number,
        "product_name": "string",
        "category": one of ["Crewneck T-shirts","Hoodies","Polo T-shirt","Boxer Brief","Boxer Shorts","Sweatshirts","Jogger Pants","Boys Top & Bottom","Women Pyjama Set","Women top & Shorts","Ladies Pyjama Set","Ladies Top & Shorts","Ladies Sleevless Top & Shorts","Women's Tank top","Women's Camisole"],
        "zipper": boolean,
        "logo_embroidery": boolean,
        "size": "2XL or 3XL"
    }"""
    
    try:
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        print("Raw Gemini Response:", response.text)  # Debug log
        
        # Try to extract JSON from the response
        try:
            # Look for JSON-like content in the response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return [data]
            else:
                print("No JSON found in response")  # Debug log
                return [{
                    "gender": "men",
                    "quantity_in_gms": 0,
                    "product_name": "",
                    "category": "Crewneck T-shirts",
                    "zipper": False,
                    "logo_embroidery": False,
                    "size": "2XL"
                }]
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")  # Debug log
            return [{
                "gender": "men",
                "quantity_in_gms": 0,
                "product_name": "",
                "category": "Crewneck T-shirts",
                "zipper": False,
                "logo_embroidery": False,
                "size": "2XL"
            }]
    except Exception as e:
        print(f"Gemini API error: {e}")  # Debug log
        raise e

async def extract_fabric(data, base64image):
    data['category'] = data['category'].replace(" ", "-").lower()
    prints = ['Waterprint', "Puff Print", "HD Print", "Foil", "Sublimation", "Tie Die", 'None']
    vals = list(obj[data['category']].keys())
    
    image_data = base64.b64decode(base64image)
    prompt = f"""Analyze this image and extract the following information in JSON format:
    {{
        "fabric_and_blend": one of {vals},
        "print": one of {prints}
    }}
    If print cannot fall under the given options, use 'None'.
    If fabric_and_blend is not in the list, match to the closest value."""
    
    try:
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        print("Raw Fabric Response:", response.text)  # Debug log
        
        try:
            # Look for JSON-like content in the response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                print("No JSON found in fabric response")  # Debug log
                response_data = {"fabric_and_blend": vals[0] if vals else "", "print": "None"}
        except json.JSONDecodeError as e:
            print(f"Fabric JSON parsing error: {e}")  # Debug log
            response_data = {"fabric_and_blend": vals[0] if vals else "", "print": "None"}
            
        blend = response_data.get('fabric_and_blend', vals[0] if vals else '')
        print_type = response_data.get('print', 'None')
        
        data['fabric_and_blend'] = blend
        if print_type == 'None':
            print_type = None
        data['print'] = print_type
        return data
    except Exception as e:
        print(f"Fabric extraction error: {e}")  # Debug log
        data['fabric_and_blend'] = vals[0] if vals else ''
        data['print'] = None
        return data

def closest(lst, K):
    return min(range(len(lst)), key = lambda i: abs(lst[i]-K))

def correct_out(data):
    try:
        data['category'] = data['category'].replace(" ","-").lower() if data.get('category') else "crewneck-t-shirts"
        data['fabric_and_blend'] = data['fabric_and_blend'].replace(" ","-") if data.get('fabric_and_blend') else ""
        if data.get('gender', '').lower() in ("adult",'unisex'):
            data['gender'] = 'men'
        else:
            data['gender'] = data.get('gender', 'men').lower()
        
        pp = ["140-160", "180-200", "220-240", "260-280"]
        
        if data['category'] in obj:
            if data.get('fabric_and_blend') in obj[data['category']]:
                pp = list(obj[data['category']][data['fabric_and_blend']].keys())
        
        # Handle None or invalid quantity_in_gms
        try:
            val = int(data.get('quantity_in_gms', 0))
        except (TypeError, ValueError):
            print(f"Invalid quantity_in_gms value: {data.get('quantity_in_gms')}")
            val = 0
            
        new_val = None
        mins = []
        
        for x in pp:
            x = [int(j) for j in x.split("-")]
            if val > x[0]:
                if len(x) > 1:
                    if val < x[1]:
                        new_val = "-".join([str(y) for y in x])
                else:
                    new_val = "-".join([str(y) for y in x])
            mins.append(x[0])
            
        if new_val is None:
            new_val = pp[closest(mins, val)]
            
        if data.get('print') is not None:
            data['print'] = data['print'].replace(" ", "-").lower()
            
        data['quantity_in_gms'] = new_val
        
        # Ensure all required fields exist with default values
        default_values = {
            'gender': 'men',
            'quantity_in_gms': new_val,
            'product_name': '',
            'category': 'crewneck-t-shirts',
            'zipper': False,
            'logo_embroidery': False,
            'size': '2XL'
        }
        
        for key, default_value in default_values.items():
            if key not in data or data[key] is None:
                data[key] = default_value
                
        return data
    except Exception as e:
        print(f"Error in correct_out: {str(e)}")
        # Return default structure if error occurs
        return {
            'gender': 'men',
            'quantity_in_gms': '180-200',
            'product_name': '',
            'category': 'crewneck-t-shirts',
            'zipper': False,
            'logo_embroidery': False,
            'size': '2XL',
            'fabric_and_blend': '',
            'print': None
        }

@app.get('/extract_info',response_class=HTMLResponse)
async def get_file(request:Request):
    return templates.TemplateResponse(name="index.html",context={"request":request})

def encode_image(image_path=None):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def extract_info_from_excel(file_content):
    try:
        # Read Excel file from bytes with explicit engine for .xlsm files
        df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
        
        # Debug logging
        print("Excel columns:", df.columns.tolist())
        print("Excel data shape:", df.shape)
        
        # Drop empty rows and reset index
        df = df.dropna(how='all').reset_index(drop=True)
        
        # If DataFrame is empty after dropping empty rows, return default
        if df.empty:
            print("No data found in Excel file after removing empty rows")
            return [{
                "gender": "men",
                "quantity_in_gms": 0,
                "product_name": "",
                "category": "Crewneck T-shirts",
                "zipper": False,
                "logo_embroidery": False,
                "size": "2XL"
            }]
        
        # Convert DataFrame to dictionary
        data = df.to_dict(orient='records')
        
        # Process the data to match the expected format
        processed_data = []
        for row in data:
            try:
                # Skip rows where all values are empty or default
                if all(v == '' or v is None or v == 0 or v == 'men' or v == 'Crewneck T-shirts' or v == '2XL' 
                       for k, v in row.items() if k in ['gender', 'quantity_in_gms', 'product_name', 'category', 'size']):
                    continue
                    
                processed_row = {
                    "gender": str(row.get('gender', 'men')).lower(),
                    "quantity_in_gms": int(row.get('quantity_in_gms', 0)),
                    "product_name": str(row.get('product_name', '')),
                    "category": str(row.get('category', 'Crewneck T-shirts')),
                    "zipper": bool(row.get('zipper', False)),
                    "logo_embroidery": bool(row.get('logo_embroidery', False)),
                    "size": str(row.get('size', '2XL'))
                }
                processed_data.append(processed_row)
            except Exception as row_error:
                print(f"Error processing row: {row_error}")
                continue
        
        # If no valid data was processed, return default
        if not processed_data:
            print("No valid data found in Excel file after processing")
            return [{
                "gender": "men",
                "quantity_in_gms": 0,
                "product_name": "",
                "category": "Crewneck T-shirts",
                "zipper": False,
                "logo_embroidery": False,
                "size": "2XL"
            }]
            
        # Remove duplicates based on all fields
        unique_data = []
        seen = set()
        for item in processed_data:
            # Create a tuple of all values for comparison
            item_tuple = tuple(item.values())
            if item_tuple not in seen:
                seen.add(item_tuple)
                unique_data.append(item)
        
        return unique_data
    except Exception as e:
        print(f"Excel processing error: {e}")
        return [{
            "gender": "men",
            "quantity_in_gms": 0,
            "product_name": "",
            "category": "Crewneck T-shirts",
            "zipper": False,
            "logo_embroidery": False,
            "size": "2XL"
        }]

@app.post('/extract_info',response_class=JSONResponse)
async def get_file(request: Request):
    try:
        form=File_request(request)
        await form.load_data()
        file=form.upload_file
        
        # Get the actual file from the form
        form_data = await request.form()
        uploaded_file = form_data.get("file")
        
        if not uploaded_file:
            return JSONResponse(content={"error": "No file uploaded"}, status_code=400)
            
        # Get the filename from the uploaded file
        filename = uploaded_file.filename
        print("Uploaded filename:", filename)
        
        # Extract file extension
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        print("Detected file extension:", file_extension)
        
        # List of supported Excel formats
        excel_formats = ['xlsx', 'xls', 'xlsm']
        
        # Check if the file extension is in our supported formats
        if file_extension == 'pdf' or file_extension in excel_formats:
            print("File type is supported:", file_extension)
            # Create a temporary directory if it doesn't exist
            temp_dir = os.path.join(os.getcwd(), 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            if file_extension == 'pdf':
                # Handle PDF file
                pdf_path = os.path.join(temp_dir, 'tec_pack.pdf')
                jpeg_path = os.path.join(temp_dir, 'tec_pack.pdf.jpeg')
                
                with open(pdf_path, 'wb') as f:
                    f.write(file)
                    
                doc = fitz.open(pdf_path)
                page = doc.load_page(0)
                pixmap = page.get_pixmap()
                pixmap.set_dpi(512,512)
                img = pixmap.tobytes()
                
                with open(jpeg_path, 'wb') as f:
                    f.write(img)
                    f.close()
                    
                item = encode_image(image_path=jpeg_path)
                resp = await extract_info(base64_image=item)
                resp = resp[0]
                resp = await extract_fabric(resp, item)
                resp = correct_out(resp)
                
                # Clean up temporary files
                try:
                    os.remove(pdf_path)
                    os.remove(jpeg_path)
                except:
                    pass
                    
                return JSONResponse(content=resp,status_code=200)
            
            else:
                # Handle Excel file
                try:
                    resp = await extract_info_from_excel(file)
                    return JSONResponse(content=resp, status_code=200)
                except Exception as e:
                    print("Error processing Excel file:", str(e))
                    return JSONResponse(content={"error": f"Error processing Excel file: {str(e)}"}, status_code=400)
                
        else:
            print("Unsupported file extension:", file_extension)
            return JSONResponse(content={"error": f"Unsupported file format. Please upload PDF or Excel files (supported formats: .pdf, .xlsx, .xls, .xlsm). Detected extension: {file_extension}"}, status_code=400)
            
    except Exception as e:
        print("General error:", str(e))
        return JSONResponse(content=str(e),status_code=400)