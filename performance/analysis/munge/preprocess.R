azure.order = c("a1","a2","a3","a4",
                "d1","d2","d3","d4",
                "d11","d12","d13",
                "d1_v2","d2_v2","d3_v2","d4_v2",
                "d11_v2","d12_v2","d13_v2")

aws.order = c("micro", "small", "medium", "large", "xlarge", "2xlarge")
col.headers = c("VM Type","VM Size", "compiler", "compress", "crypto", "derby", "mpegaudio", "scimark.large","scimark.small","serial","startup","sunflow","xml","Overall")

data.azure = full.output %>%
  filter(provider == "azure") %>%
  select(-provider) %>%
  mutate(overall=gm.rowmeans(.[,4:14])) %>%
  mutate(vm_size = factor(vm_size, levels=azure.order))

data.aws = full.output %>%
  filter(provider == "aws") %>%
  select(-provider) %>%
  mutate(overall=gm.rowmeans(.[,4:14])) %>%
  mutate(vm_size = factor(vm_size, levels=aws.order))

data.azure = droplevels(data.azure)
data.aws = droplevels(data.aws)

data.azure.single.thread = azure.single.thread %>%
  select(-provider) %>%
  mutate(overall=gm.rowmeans(.[,4:14])) %>%
  mutate(vm_size = factor(vm_size, levels=azure.order))
