from typing import Optional, Literal
from pydantic import BaseModel, Field

class Position(BaseModel):
    x: float
    y: float
    width: float
    height: float

class RGBColor(BaseModel):
    red: float
    green: float
    blue: float

class TextStyle(BaseModel):
    fontFamily: str = Field(description="Font family of the text, e.g. 'Arial'")
    fontSize: float = Field(description="Font size of the text, e.g. 12")
    bold: bool = Field(description="Whether the text is bold")
    italic: bool = Field(description="Whether the text is italic")
    underline: bool = Field(description="Whether the text is underlined")
    foregroundColor: RGBColor = Field(description="Foreground RGB color of the text (e.g., {'red': 0, 'green': 0, 'blue': 0})")
    backgroundColor: RGBColor = Field(description="Background RGB color of the text (e.g., {'red': 0, 'green': 0, 'blue': 0})")

class ParagraphStyle(BaseModel):
    alignment: Optional[Literal['START', 'CENTER', 'END', 'JUSTIFIED']] = Field(None, description="Text alignment")
    lineSpacing: Optional[int] = Field(None, description="Line spacing in percentage (e.g., 150 for 1.5 line spacing)")
    spaceAbove: Optional[float] = Field(None, description="Space above paragraph in points")
    spaceBelow: Optional[float] = Field(None, description="Space below paragraph in points")
    indentFirstLine: Optional[float] = Field(None, description="First line indent in points")
    indentStart: Optional[float] = Field(None, description="Left indent in points")
    indentEnd: Optional[float] = Field(None, description="Right indent in points")
    direction: Optional[Literal['LEFT_TO_RIGHT', 'RIGHT_TO_LEFT']] = Field(None, description="Text direction")
    spacingMode: Optional[Literal['NEVER_COLLAPSE', 'COLLAPSE_LISTS']] = Field(None, description="Spacing mode") 