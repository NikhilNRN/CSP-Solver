import re
import operator
import copy
import sys

mathOperations = {">": operator.gt, "<": operator.lt, "=": operator.eq, "!": operator.ne}

def main():
    global counterVar
    counterVar = 0
    varList = {}
    with open(sys.argv[1], errors='ignore') as input_file:
        for i, lineText in enumerate(input_file):
            lineText = re.sub(r'\n', '', lineText)
            lineText = re.sub(r'[ \t]+$', '', lineText)
            var = Var()
            var.label = lineText[0]
            temp = []
            for j in lineText[3:].split(' '):
                temp.append(int(j))
            var.domain = temp
            var.assignment = None
            varList[var.label] = var

    constraints = []
    with open(sys.argv[2], errors='ignore') as input_file:
        for i, lineText in enumerate(input_file):
            lineText = re.sub(r'\n', '', lineText)
            lineText = re.sub(r'[ \t]+$', '', lineText)
            constraints.append((lineText[0], lineText[2], lineText[4]))

    if sys.argv[3] == "none":
        forwardChecking = False
    else:
        forwardChecking = True

    track = backTracking({}, varList, constraints, forwardChecking)
    if track is not False:
        x = 0
        counterVar += 1
        print(counterVar, ". ", end="", sep="")
        for v in track.keys():
            if x is len(track.keys()) - 1:
                print(v, "=", track[v], " solution", sep="")
            else:
                print(v, "=", track[v], ", ", end="", sep="")
            x += 1


class Var():
    label = None
    domain = None
    assignment = None


counterVar = 0


def backTracking(assigned, varList, constraints, forwardChecking):
    global counterVar
    if all(variable.assignment != None for variable in varList.values()):
        return assigned

    varFile = unassignedVariable(varList, constraints)
    orderedDomain = sortDomain(varList, constraints, varFile)

    for item in orderedDomain:
        for num in item:
            num = int(num)
            flag = True
            for conFile in constraints:
                if conFile[0] is varList[varFile].label:
                    if varList[conFile[2]].assignment is None:
                        continue
                    else:
                        flag = mathOperations[conFile[1]](num, int(varList[conFile[2]].assignment))

                elif conFile[2] is varList[varFile].label:
                    if varList[conFile[0]].assignment is None:
                        continue
                    else:
                        flag = mathOperations[conFile[1]](int(varList[conFile[0]].assignment), num)

                if flag is False:
                    c = 0
                    counterVar += 1
                    print(counterVar, ". ", end="", sep="")
                    for v in assigned.keys():
                        if c is len(assigned.keys()) - 1:
                            print(v, "=", assigned[v], ", ", end="", sep="")
                            print(varList[varFile].label, "=", num, " failure", sep="")
                        else:
                            print(v, "=", assigned[v], ", ", end="", sep="")
                        c += 1
                    if counterVar >= 30:
                        SystemExit
                    break

            if flag is True:
                varList[varFile].assignment = num
                assigned[varFile] = num
                varListResult = None
                if forwardChecking is True:
                    varListResult = forwardChecking(copy.deepcopy(varList), constraints, varFile)
                    for variable in varListResult.values():
                        if len(variable.domain) is 0:
                            c = 0
                            counterVar += 1
                            print(counterVar, ". ", end="", sep="")
                            for v in assigned.keys():
                                if c is len(assigned.keys()) - 1:
                                    print(varList[varFile].label, "=", num, " failure", sep="")
                                else:
                                    print(v, "=", assigned[v], ", ", end="", sep="")
                                c += 1
                            if counterVar >= 30:
                                SystemExit
                            continue
                else:
                    varListResult = varList

                result = backTracking(assigned, varListResult, constraints, forwardChecking)
                if result is not False:
                    return result
                varList[varFile].assignment = None
                assigned.pop(varFile)

    return False


def forwardChecking(variableList, constraints, var):
    assignedValue = variableList[var].assignment
    for conFile in constraints:
        if conFile[0] is variableList[var].label:
            if variableList[conFile[2]].assignment is None:
                removalList = []
                for value in variableList[conFile[2]].domain:
                    if mathOperations[conFile[1]](assignedValue, value) is False:
                        removalList.append(value)

                for r in removalList:
                    variableList[conFile[2]].domain.remove(r)

        elif conFile[2] is variableList[var].label:
            if variableList[conFile[0]].assignment is None:
                removalList = []
                for value in variableList[conFile[0]].domain:
                    if mathOperations[conFile[1]](value, assignedValue) is False:
                        removalList.append(value)
                for r in removalList:
                    variableList[conFile[0]].domain.remove(r)

    return variableList


def unassignedVariable(variables, constraints):
    var = None
    varList = []
    for item in variables.keys():
        if variables[item].assignment == None:
            if var == None:
                var = item
                varList.append(item)
            elif len(variables[var].domain) > len(variables[item].domain):
                var = item
                varList = [item]
            elif len(variables[var].domain) == len(variables[item].domain):
                varCount = 0
                variableCount = 0
                varCount += sum(1 for i in constraints if i[0] == variables[var].label and variables[i[2]].assignment == None)
                varCount += sum(1 for i in constraints if variables[i[0]].assignment == None and i[2] == variables[var].label)
                variableCount += sum(1 for i in constraints if i[0] == variables[item].label and variables[i[2]].assignment == None)
                variableCount += sum(1 for i in constraints if variables[i[0]].assignment == None and i[2] == variables[item].label)
                if varCount < variableCount:
                    var = item
                    varList = [item]
                elif varCount == variableCount:
                    varList.append(item)

    return var


def sortDomain(variableList, constraints, var):
    constraintValues = {}
    for val in variableList[var].domain:
        val = int(val)
        temp = 0
        for cons in constraints:
            if cons[0] is variableList[var].label and variableList[cons[2]].assignment is None:
                for compValue in variableList[cons[2]].domain:
                    if not mathOperations[cons[1]](val, int(compValue)):
                        temp += 1
            elif variableList[cons[0]].assignment is None and cons[2] == variableList[var].label:
                for compValue in variableList[cons[0]].domain:
                    if not mathOperations[cons[1]](int(compValue), val):
                        temp += 1

        if temp in constraintValues:
            constraintValues[temp].append(int(val))
        else:
            constraintValues[temp] = [int(val)]

    domainOrdered = []
    for s in sorted(constraintValues.keys()):
        domainOrdered.append(constraintValues[s])

    return domainOrdered

if __name__ == "__main__":
    main()