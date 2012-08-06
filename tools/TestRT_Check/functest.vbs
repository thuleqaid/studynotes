Sub Import()
    Dim i, x, startrow, stoprow As Integer
    'ファイルパスの開始・終了行
    startrow = -1
    stoprow = -1
    i = 1
    While stoprow < 0
        If Trim(ThisWorkbook.Sheets(1).Cells(i, 1).Value) = "ファイル：" And Trim(ThisWorkbook.Sheets(1).Cells(i, 2).Value) <> "" Then
            If startrow < 0 Then
                startrow = i
            End If
        Else
            If startrow > 0 Then
                stoprow = i - 1
            End If
        End If
        i = i + 1
    Wend
    '前回結果クリア
    If ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row > stoprow Then
        ThisWorkbook.Sheets(1).Rows((stoprow + 1) & ":" & ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row).Select
        Selection.Delete Shift:=xlUp
    End If
    '結果出力
    x = stoprow + 5
    For i = startrow To stoprow
        x = CalcSection(Trim(ThisWorkbook.Sheets(1).Cells(i, 2).Value), Int(x)) + 1
    Next i
End Sub

Sub Export()
    Dim i, startrow As Integer
    'ファイルパスの開始・終了行
    startrow = -1
    i = 1
    While startrow < 0
        If Trim(ThisWorkbook.Sheets(1).Cells(i, 1).Value) = "ファイル：" Then
            If startrow < 0 Then
                startrow = i
            End If
        End If
        i = i + 1
    Wend
    
    Filename = ThisWorkbook.Path & "\xls.txt"
    Open Filename For Output As #1
    Call ExportSheet(ThisWorkbook.Sheets(1).Name, startrow)
    Close #1
    Rem Filename = ThisWorkbook.Path & "\design2src.exe definition.txt design.txt"
    Rem TaskID = Shell(Filename, 1)
    Rem hProc = OpenProcess(&H400, False, TaskID)
    Rem Do
    Rem     GetExitCodeProcess hProc, lExitCode
    Rem Loop While lExitCode = &H103
End Sub

Sub Clear()
    Dim i, x, startrow, stoprow As Integer
    'ファイルパスの開始・終了行
    startrow = -1
    stoprow = -1
    i = 1
    While stoprow < 0
        If Trim(ThisWorkbook.Sheets(1).Cells(i, 1).Value) = "ファイル：" Then
            ThisWorkbook.Sheets(1).Cells(i, 2).Value = ""
            If startrow < 0 Then
                startrow = i
            End If
        Else
            If startrow > 0 Then
                stoprow = i - 1
            End If
        End If
        i = i + 1
    Wend
    '前回結果クリア
    If ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row > stoprow Then
        ThisWorkbook.Sheets(1).Rows((stoprow + 1) & ":" & ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row).Select
        Selection.Delete Shift:=xlUp
    End If
End Sub

Sub ExportSheet(sheetname, startrow)
    Dim numrows As Long, numcols As Integer
    Dim r As Long, c As Integer
    Dim data
    numrows = Sheets(sheetname).Cells.SpecialCells(xlLastCell).row         '最后一行
    numcols = Sheets(sheetname).Cells.SpecialCells(xlLastCell).Column      '最后一列
    For r = startrow To numrows
        For c = 1 To numcols
            data = Trim(Sheets(sheetname).Cells(r, c).Value)
            If IsEmpty(Sheets(sheetname).Cells(r, c)) Then data = ""
            If c <> numcols Then
                Print #1, data;
                Print #1, vbTab;
            Else
                Print #1, data
            End If
        Next c
    Next r
End Sub

Function CalcSection(xFilename As String, iOutRow As Integer) As Integer
    Dim strFunc As String
    Dim i, j, k, l, m As Integer
    Dim bSect, bFilename, bFunc, bLineNo As Boolean
    Dim wkb As Workbook
    bFilename = True    'ファイル名出力
    bFunc = True        '関数名出力
    bLineNo = False     '行番号出力
    k = iOutRow
    Set wkb = Workbooks.Open(Filename:=xFilename)
    '単体テスト報告書をチェック
    'シート順：「表紙」、「改訂履歴」、「概要」、「フローチャート」、「テストケース」
    If wkb.Sheets.Count >= 5 And Trim(wkb.Sheets(3).Cells(2, 2).Value) = "検査関数" Then
        If bFilename Then
            'ファイル名出力
            ThisWorkbook.Sheets(1).Cells(k, 1).Value = xFilename
            k = k + 1
        End If
        If bFunc Then
            '関数名出力
            strFunc = Trim(wkb.Sheets(3).Cells(2, 3).Value)
            If Right(strFunc, 2) = "()" Then
                strFunc = Left(strFunc, Len(strFunc) - 2)
                ThisWorkbook.Sheets(1).Cells(k, 2).Value = strFunc
                k = k + 1
            End If
        End If
        '単体テスト報告書の5番目シートからはテストデータ
        For i = 5 To wkb.Sheets.Count
            bSect = False
            l = 0 ' F列で"結果"の箇数
            ll = 0 ' B列で"終了"の箇数
            m = k
            'シート名出力
            ThisWorkbook.Sheets(1).Cells(k, 3).Value = wkb.Sheets(i).Name
            k = k + 1
            For j = 1 To wkb.Sheets(i).Cells.SpecialCells(xlLastCell).row
                If bSect Then
                    If Trim(wkb.Sheets(i).Cells(j, 2).Value) = "終了" Then
                        bSect = False
                        ll = ll + 1
                        If bLineNo Then
                            ThisWorkbook.Sheets(1).Cells(m, 3 + l * 2).Value = j
                        End If
                        If l >= 3 Or ll >= 4 Then
                            Exit For
                        End If
                    Else
                        If Trim(wkb.Sheets(i).Cells(j, 2).Value) = "-" And Trim(wkb.Sheets(i).Cells(j, 6).Value) = "-" Then
                            '空行
                        Else
                            If l = 1 Then   '本関数の引数
                                ThisWorkbook.Sheets(1).Cells(k, 4).Value = Trim(wkb.Sheets(i).Cells(j, 2).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 5).Value = Trim(wkb.Sheets(i).Cells(j, 4).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 6).Value = Trim(wkb.Sheets(i).Cells(j, 5).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 7).Value = Trim(wkb.Sheets(i).Cells(j, 6).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 8).Value = Trim(wkb.Sheets(i).Cells(j, 3).Value)
                                If ThisWorkbook.Sheets(1).Cells(k, 5).Value Like "[!']'" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 5).Value = "'" + ThisWorkbook.Sheets(1).Cells(k, 5).Value
                                End If
                                If ThisWorkbook.Sheets(1).Cells(k, 6).Value Like "[!']'" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 6).Value = "'" + ThisWorkbook.Sheets(1).Cells(k, 6).Value
                                End If
                                k = k + 1
                            ElseIf l = 2 Then   '外部変数
                                If Trim(wkb.Sheets(i).Cells(j, 3).Value) = "-" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 4).Value = Trim(wkb.Sheets(i).Cells(j, 2).Value)
                                Else
                                    ThisWorkbook.Sheets(1).Cells(k, 4).Value = Trim(wkb.Sheets(i).Cells(j, 2).Value) & "." & Trim(wkb.Sheets(i).Cells(j, 3).Value)
                                End If
                                ThisWorkbook.Sheets(1).Cells(k, 5).Value = Trim(wkb.Sheets(i).Cells(j, 4).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 6).Value = Trim(wkb.Sheets(i).Cells(j, 5).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 7).Value = Trim(wkb.Sheets(i).Cells(j, 6).Value)
                                If ThisWorkbook.Sheets(1).Cells(k, 5).Value Like "[!']'" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 5).Value = "''" + ThisWorkbook.Sheets(1).Cells(k, 5).Value
                                End If
                                If ThisWorkbook.Sheets(1).Cells(k, 6).Value Like "[!']'" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 6).Value = "''" + ThisWorkbook.Sheets(1).Cells(k, 6).Value
                                End If
                                k = k + 1
                            ElseIf l = 3 Then   '本関数の処理結果
                                ThisWorkbook.Sheets(1).Cells(k, 4).Value = Trim(wkb.Sheets(i).Cells(j, 2).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 5).Value = Trim(wkb.Sheets(i).Cells(j, 4).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 6).Value = Trim(wkb.Sheets(i).Cells(j, 5).Value)
                                ThisWorkbook.Sheets(1).Cells(k, 7).Value = Trim(wkb.Sheets(i).Cells(j, 6).Value)
                                If ThisWorkbook.Sheets(1).Cells(k, 5).Value Like "[!']'" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 5).Value = "'" + ThisWorkbook.Sheets(1).Cells(k, 5).Value
                                End If
                                If ThisWorkbook.Sheets(1).Cells(k, 6).Value Like "[!']'" Then
                                    ThisWorkbook.Sheets(1).Cells(k, 6).Value = "'" + ThisWorkbook.Sheets(1).Cells(k, 6).Value
                                End If
                                k = k + 1
                            End If
                        End If
                    End If
                Else
                    If Trim(wkb.Sheets(i).Cells(j, 6).Value) = "結果" Then
                        l = l + 1
                        bSect = True
                        If bLineNo Then
                            ThisWorkbook.Sheets(1).Cells(m, 2 + 2 * l).Value = j
                        End If
                    End If
                    If Trim(wkb.Sheets(i).Cells(j, 2).Value) = "終了" Then
                        ll = ll + 1
                    End If
                End If
            Next j
            If l < 3 Or ll < 4 Then
                ThisWorkbook.Sheets(1).Cells(iOutRow, 10).Value = "Error"
            End If
        Next i
    Else
        'エラーファイル名出力
        ThisWorkbook.Sheets(1).Cells(k, 1).Value = xFilename
        ThisWorkbook.Sheets(1).Cells(k, 10).Value = "Error"
        k = k + 1
    End If
    wkb.Close
    CalcSection = k
End Function

