import re, os, ntpath, copy


def getOtherSideStr(inputStr):
    leftList = ['_L_', '_LU_', '_LD_', '_LF_', '_LB_', '_LUF_', '_LUB_']
    rightList = ['_R_', '_RU_', '_RD_', '_RF_', '_RB_', '_RUF_', '_RUB_']

    for i in range(len(leftList)):
        if inputStr.find(leftList[i]) != -1:
            return inputStr.replace(leftList[i], rightList[i])
        elif inputStr.find(rightList[i]) != -1:
            return inputStr.replace(rightList[i], leftList[i])
    return inputStr


def findStringSamePart( src, trg ):

    def getSeparatedStringList( str1 ):
        def cmpByLength( first, second ):
            if len( first ) > len( second ):
                return -1
            elif len( first ) < len( second ):
                return 1
            return 0
        lenStr = len( str1 )
        sepTargets = []
        for numStr in range( 1, lenStr ):
            for i in range( lenStr-numStr+1 ):
                sepTargets.append( str1[i:numStr+i] )
        sepTargets = list( set( sepTargets ) )
        sepTargets.sort( cmpByLength )
        return sepTargets

    def getSameList( srcStr, targetStr ):
        resultStrs = []
        separatedStrs = getSeparatedStringList(srcStr)

        for sepStr in separatedStrs:
            findIndex = targetStr.find( sepStr )
            if findIndex == -1: continue
            lastIndex = findIndex + len( sepStr )

            findIndexSrc = srcStr.find(sepStr)
            lastIndexSrc = findIndexSrc + len( sepStr )

            srcStrStartPart = srcStr[:findIndexSrc]
            srcStrEndPart = srcStr[lastIndexSrc:]
            targetStrStartPart = targetStr[:findIndex]
            targetStrEndPart   = targetStr[lastIndex:]

            resultStrs.append(sepStr)
            if targetStrStartPart:
                resultStrs = getSameList( srcStrStartPart, targetStrStartPart ) + resultStrs
            if targetStrEndPart:
                resultStrs += getSameList( srcStrEndPart, targetStrEndPart )
            break
        return resultStrs

    def separateByList( srcStrList, targetStr ):
        copySrcStrList = copy.copy(srcStrList)
        resultList = []
        srcStr = copySrcStrList.pop( 0 )
        findIndex = targetStr.find( srcStr )
        endIndex = findIndex + len( srcStr )
        firstPart = targetStr[:findIndex]
        secondPart = targetStr[endIndex:]
        if firstPart: resultList.append( firstPart )
        else: resultList.append( '' )
        resultList.append( srcStr )
        if copySrcStrList:
            resultList += separateByList( copySrcStrList, secondPart )
        else:
            resultList.append( secondPart )
        return resultList

    sameList = getSameList( src, trg )
    srcResults = separateByList( sameList, src )
    trgResults = separateByList( sameList, trg )

    results = []
    for i in range( len( srcResults ) ):
        if srcResults[i] == trgResults[i]:
            if srcResults[i]: results.append( srcResults[i] )
        else:
            results.append( [srcResults[i], trgResults[i]] )
    return results


