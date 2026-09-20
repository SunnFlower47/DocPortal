Dim inPath, outPath, objWord, objDoc
If WScript.Arguments.Count < 2 Then
    WScript.Quit 1
End If
inPath = WScript.Arguments(0)
outPath = WScript.Arguments(1)

On Error Resume Next
Set objWord = CreateObject("Word.Application")
If Err.Number <> 0 Then
    WScript.Quit 2
End If

objWord.Visible = False
objWord.DisplayAlerts = 0

Set objDoc = objWord.Documents.Open(inPath, False, True)
If Err.Number <> 0 Then
    objWord.Quit 0
    WScript.Quit 3
End If

' 17 = wdExportFormatPDF
objDoc.ExportAsFixedFormat outPath, 17
objDoc.Close 0
objWord.Quit 0

If Err.Number <> 0 Then
    WScript.Quit 4
End If

WScript.Quit 0
