import io
import pandas as pd

def generate_excel_bytes(data):
    """Membuat file Excel dalam bentuk bytes (RAM) tanpa menyimpan ke disk"""
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data_Ekstraksi')
        worksheet = writer.sheets['Data_Ekstraksi']
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 14)
    output.seek(0)
    return output
