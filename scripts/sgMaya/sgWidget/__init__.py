import ntpath, os, re

def getClassNameConvertedString( path ):

    filename = os.path.splitext(ntpath.split(path)[-1])[0]
    if filename == '__init__':
        filename = ntpath.split( os.path.dirname( path ) )[-1]

    f = open(path, 'r')
    data = f.read()
    f.close()

    patten = re.compile('class\s[a-zA-Z]\w+')
    results = patten.findall(data)

    classNames = []
    resultsList = []
    for result in results:
        className = result.split(' ')[-1]
        pattenName = '[^A-Za-z0-9_]%s[^A-Za-z0-9_]' % className
        patten_second = re.compile(pattenName)

        results_second = list(set(patten_second.findall(data)))

        print className, results_second

        classNames.append(className)
        resultsList.append(results_second)


    for i in range(len(classNames)):
        className = classNames[i]
        for result in resultsList[i]:
            replaceString = result[0] + filename + '_' + className + result[-1]
            data = data.replace(result, replaceString)

    savePath = os.path.dirname(path) + "/convertedScript.txt"
    f = open(savePath, 'w')
    f.write(data)
    f.close()

    os.system(savePath)

