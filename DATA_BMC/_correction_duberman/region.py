import pickle, cv2, sys, numpy as np
P = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
def region(pi, la, lb, out):
    L = P[pi]['lines']; lb = min(lb, len(L)-1)
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg')
    y0 = int(L[la]['y0']*S) - 8; y1 = int(L[lb]['y1']*S) + 6
    cv2.imwrite(out, im[max(0,y0):y1])
if __name__ == '__main__':
    pi, la, lb, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    region(pi, la, lb, out)
