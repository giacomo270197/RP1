import sys

def split_string(line):
  strings = []
  quotes = False
  tmp = ""
  for x in line:
    if x == '"':
      quotes = not quotes
    if x == ',':
      if not quotes:
        strings.append(tmp)
        tmp = ""
      else:
        tmp = "{}{}".format(tmp, x)
    else:
      tmp = "{}{}".format(tmp, x)
  strings.append(tmp)
  return strings

interval = 0.0

with open(sys.argv[1], "r") as file_read:
  with open(sys.argv[2], "w") as file_write:
    file_read.readline()
    for line in file_read:
      line = split_string(line)[:-1]
      line = [x.strip('"') for x in line]
      tmp = float(line[1])
      line[1] = tmp - interval
      interval = tmp
      line[-1] = int(line[-1])
      file_write.write(",".join([str(x) for x in line]))
      file_write.write("\n")
