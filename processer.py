import re, os

def read_file(filename):
  global result_dict
  result_dict = dict()
  with open(filename, 'r') as fin:
    content = fin.read()
  sections = content.split("# ")
  for sec in sections:
    split_sec = sec.split('\n', 1)
    file_id = split_sec[0]
    if len(split_sec) > 1:
      file_content = split_sec[1]
      print file_id
      # print file_content
      extra = re.search(r"ca\d\d\d\d\d\d", file_content)
      extracted = file_content[:extra.start()]
      print extracted
      result_dict[file_id] = extracted

def write_separate_file():
  if not os.path.exists('cacm/'):
    os.mkdir('cacm/')

  for file_id in result_dict:
    fout = open("cacm/" + "CACM-" + file_id.zfill(4) + ".txt", 'w')
    fout.write(result_dict[file_id])

def main():
  read_file('test-collection/cacm_stem.txt')
  write_separate_file()

if __name__ == '__main__':
  main()