from importlib.resources import path


lines = []

PATH = r'F:\rasa_chat\data\historico-nombres.txt'
NEWPATH = r'F:\rasa_chat\data\newnames.txt'
with open(PATH, 'r', encoding="utf8") as file:
    lines = file.readlines()

count = 0
for line in lines:
    lines[count] = line.capitalize()
    count += 1

linesSet = set(lines)
newFile = open(NEWPATH, 'w', encoding="utf8")
count = 0
for line in linesSet:
    lines[count] = line.split('\\')[0].capitalize()
    if line.find(r"(") < 0 and line.find(r'"') < 0:
        newFile.write(f"{lines[count]}\n")
    # lines[count] = line.replace("'", "")
    # count += 1


newFile.close()
# with open(PATH, 'w', encoding="utf8") as file:
#     file.write(linesStr)