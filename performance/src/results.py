import re

f = open('testoutput', 'r')
output = ''
# ssh_stdout = f.readlines()
for line in f.readlines():
    output += line
# result = [x for x in ssh_stdout if x.startswith('Score on') or x.startswith('Noncompliant composite')]
scorepat = re.compile('Score on ([a-z]+): (.+)\n')
overallpat = re.compile('Noncompliant composite result: (.+)\n')
results = dict(scorepat.findall(output))
results['overall'] = overallpat.search(output).group(1)
print(output)
print(results)
# print(results)
