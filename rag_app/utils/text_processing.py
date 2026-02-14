import fitz  # PyMuPDF
from fastapi import UploadFile
import docx
import io

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Yüklenen dosyalardan metin içeriğini çıkarır.
    Desteklenen formatlar: .pdf, .docx, .txt
    
    Args:
        file (UploadFile): FastAPI dosya nesnesi
        
    Returns:
        str: Dosyanın metin içeriği
    """
    filename = file.filename.lower()
    content = await file.read()
    
    text = ""
    
    # PDF İşleme
    if filename.endswith(".pdf"):
        # PyMuPDF (fitz) kullanarak stream'den okuma
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
            
    # DOCX İşleme
    elif filename.endswith(".docx"):
        # python-docx kütüphanesi BytesIO kullanır
        doc = docx.Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
            
    # TXT İşleme 
    elif filename.endswith(".txt"):
        # Farklı encoding denemeleri
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except:
                text = str(content) # Fallback
                
    elif filename.endswith(".doc"):
        raise ValueError(f".doc formatı desteklenmiyor, lütfen .docx'e çevirin: {filename}")
        
    return text

def chunk_text(text: str, chunk_size=500, overlap=50) -> list[str]:
    """
    Metni belirtilen boyutlarda parçalara (chunk) böler.
    Overlap (örtüşme) sayesinde bağlam kaybı azaltılır.
    
    Args:
        text (str): İşlenecek ham metin
        chunk_size (int): Her parçanın maksimum karakter sayısı
        overlap (int): Parçalar arasındaki örtüşme miktarı
        
    Returns:
        list[str]: Metin parçaları listesi
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Bir sonraki parça için başlangıcı overlap kadar geri alarak ilerle
        start += chunk_size - overlap
        
    return chunks
