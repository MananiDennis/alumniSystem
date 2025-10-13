from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import pandas as pd, io
from typing import List
from src.services.alumni_collector import AlumniCollector
from src.api.utils import format_alumni

router = APIRouter(prefix="", tags=["upload"])  # root-level endpoints


@router.post("/upload-names")
async def upload_names_file(file: UploadFile = File(...), auto_collect: bool = False, user_email: str = Depends(lambda: "admin")):
    try:
        if not file.filename.endswith((".xlsx", ".xls", ".csv")):
            raise HTTPException(status_code=400, detail="File must be .xlsx, .xls, or .csv")

        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(await file.read()))
        else:
            df = pd.read_excel(io.BytesIO(await file.read()))

        for col in ['GIVEN NAME', 'FIRST NAME']:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

        names = [f"{row['GIVEN NAME']} {row['FIRST NAME']}".strip() for _, row in df.iterrows() if pd.notna(row['GIVEN NAME']) and pd.notna(row['FIRST NAME'])]
        profiles = []
        if auto_collect and names:
            try:
                collector = AlumniCollector()
                profiles = collector.collect_alumni(names)
                collector.close()
            except Exception as collect_error:
                print(f"Auto-collection failed: {collect_error}")

        return {"success": True, "names": names, "count": len(names), "collected_profiles": [format_alumni(p) for p in profiles], "profiles_collected": len(profiles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
