import io
import pandas as pd

def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Doors with Hardware") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        # Freeze header row
        ws.freeze_panes = "A2"
        # Auto width (approx)
        for col_cells in ws.columns:
            length = max(len(str(cell.value or "")) for cell in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max(12, length + 2), 50)
    return output.getvalue()
