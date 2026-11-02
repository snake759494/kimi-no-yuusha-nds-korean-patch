def dec(b):
  out=[];i=0
  while i<len(b):
    c=b[i]
    if c==0x1b:out.append('{%02x}'%b[i+1]);i+=2
    elif c==0x0a:out.append('\n');i+=1
    elif c<0x20:out.append('{c%02x}'%c);i+=1
    elif c<0x80 or 0xa1<=c<=0xdf:out.append(bytes([c]).decode('cp932'));i+=1
    else:out.append(b[i:i+2].decode('cp932'));i+=2
  return ''.join(out)
