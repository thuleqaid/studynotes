Sub Import()
    Dim i, x, startrow, stoprow As Integer
    '�t�@�C���p�X�̊J�n�E�I���s
    startrow = -1
    stoprow = -1
    i = 1
    While stoprow < 0
        If Trim(ThisWorkbook.Sheets(1).Cells(i, 1).Value) = "�t�@�C���F" And Trim(ThisWorkbook.Sheets(1).Cells(i, 2).Value) <> "" Then
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
    '�O�񌋉ʃN���A
    If ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row > stoprow Then
        ThisWorkbook.Sheets(1).Rows((stoprow + 1) & ":" & ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row).Select
        Selection.Delete Shift:=xlUp
    End If
    '���ʏo��
    x = stoprow + 5
    For i = startrow To stoprow
        x = CalcSection(Trim(ThisWorkbook.Sheets(1).Cells(i, 2).Value), Int(x)) + 1
    Next i
End Sub

Sub Export()
    Dim i, startrow As Integer
    '�t�@�C���p�X�̊J�n�E�I���s
    startrow = -1
    i = 1
    While startrow < 0
        If Trim(ThisWorkbook.Sheets(1).Cells(i, 1).Value) = "�t�@�C���F" Then
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
    '�t�@�C���p�X�̊J�n�E�I���s
    startrow = -1
    stoprow = -1
    i = 1
    While stoprow < 0
        If Trim(ThisWorkbook.Sheets(1).Cells(i, 1).Value) = "�t�@�C���F" Then
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
    '�O�񌋉ʃN���A
    If ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row > stoprow Then
        ThisWorkbook.Sheets(1).Rows((stoprow + 1) & ":" & ThisWorkbook.Sheets(1).Cells.SpecialCells(xlLastCell).row).Select
        Selection.Delete Shift:=xlUp
    End If
End Sub

Sub ExportSheet(sheetname, startrow)
    Dim numrows As Long, numcols As Integer
    Dim r As Long, c As Integer
    Dim data
    numrows = Sheets(sheetname).Cells.SpecialCells(xlLastCell).row         '�ō@��s
    numcols = Sheets(sheetname).Cells.SpecialCells(xlLastCell).Column      '�ō@���
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
    bFilename = True    '�t�@�C�����o��
    bFunc = True        '�֐����o��
    bLineNo = False     '�s�ԍ��o��
    k = iOutRow
    Set wkb = Workbooks.Open(Filename:=xFilename)
    '�P�̃e�X�g�񍐏����`�F�b�N
    '�V�[�g���F�u�\���v�A�u���������v�A�u�T�v�v�A�u�t���[�`���[�g�v�A�u�e�X�g�P�[�X�v
    If wkb.Sheets.Count >= 5 And Trim(wkb.Sheets(3).Cells(2, 2).Value) = "�����֐�" Then
        If bFilename Then
            '�t�@�C�����o��
            ThisWorkbook.Sheets(1).Cells(k, 1).Value = xFilename
            k = k + 1
        End If
        If bFunc Then
            '�֐����o��
            strFunc = Trim(wkb.Sheets(3).Cells(2, 3).Value)
            If Right(strFunc, 2) = "()" Then
                strFunc = Left(strFunc, Len(strFunc) - 2)
                ThisWorkbook.Sheets(1).Cells(k, 2).Value = strFunc
                k = k + 1
            End If
        End If
        '�P�̃e�X�g�񍐏���5�ԖڃV�[�g����̓e�X�g�f�[�^
        For i = 5 To wkb.Sheets.Count
            bSect = False
            l = 0 ' F���"����"�̉Ӑ�
            ll = 0 ' B���"�I��"�̉Ӑ�
            m = k
            '�V�[�g���o��
            ThisWorkbook.Sheets(1).Cells(k, 3).Value = wkb.Sheets(i).Name
            k = k + 1
            For j = 1 To wkb.Sheets(i).Cells.SpecialCells(xlLastCell).row
                If bSect Then
                    If Trim(wkb.Sheets(i).Cells(j, 2).Value) = "�I��" Then
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
                            '��s
                        Else
                            If l = 1 Then   '�{�֐��̈���
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
                            ElseIf l = 2 Then   '�O���ϐ�
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
                            ElseIf l = 3 Then   '�{�֐��̏�������
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
                    If Trim(wkb.Sheets(i).Cells(j, 6).Value) = "����" Then
                        l = l + 1
                        bSect = True
                        If bLineNo Then
                            ThisWorkbook.Sheets(1).Cells(m, 2 + 2 * l).Value = j
                        End If
                    End If
                    If Trim(wkb.Sheets(i).Cells(j, 2).Value) = "�I��" Then
                        ll = ll + 1
                    End If
                End If
            Next j
            If l < 3 Or ll < 4 Then
                ThisWorkbook.Sheets(1).Cells(iOutRow, 10).Value = "Error"
            End If
        Next i
    Else
        '�G���[�t�@�C�����o��
        ThisWorkbook.Sheets(1).Cells(k, 1).Value = xFilename
        ThisWorkbook.Sheets(1).Cells(k, 10).Value = "Error"
        k = k + 1
    End If
    wkb.Close
    CalcSection = k
End Function

