#
# Cal3d mesh filter by emanuele ruffaldi
#
# Produces a JSON + Binary
#

import xcal3d
import sys
from array import array
import numpy,json

def skel2dic(s):
	o = {}
	bones = []
	for b in s.bones.values():
		bo = dict(id=b.id,pid=b.pid,name=b.name,tx=str(b.tx)[1:-1],quat=str(b.rot)[1:-1],localtx=b.localtx[1:-1],localquat=str(b.localrot)[1:-1])
		bones.append(bo)
	o.bones = bones

def mesh2dicbin(meshdata,dic,obin,maxinfluence=4,maxtransforms=52,maxtexcoords=1):

	dd = []
	stride = maxtexcoords*2+3+3+maxinfluence*2
	for m in sm.children:
		m.computestats()
		print m.name,"vertices",len(m.vertices), "affected bones",len(m.bones),"maxinfluence",m.maxinfluence,"texcoords",m.numtexcoords

		if m.maxinfluence > maxinfluence:
			print "influence remap not implemented"
			sys.exit(-1)
			m.limitinfluence(maxinfluence)
		if len(m.bones) > maxtransforms:
			print "more bones than max -> FAIL"
		if len(m.bones) < 10:
			print "small bone ref:",m.bones
		if m.numtexcoords > maxtexcoords:
			print "more texcoord than max -> skip coords"

		if False:
			bones = list(m.bones)
			oldbone2newbone = dict([(b,i) for i,b in enumerate(bones)])

			md = {}
			ad = []
			for v in m.vertices:
				ad.append(v.pos[0])
				ad.append(v.pos[1])
				ad.append(v.pos[2])
				ad.append(v.normal[0])
				ad.append(v.normal[1])
				ad.append(v.normal[2])
				ni = len(v.influences)
				# weights with pad to max
				for b,w in v.influences:
					ad.append(w)
				for i in range(ni,maxinfluence):
					ad.append(0)
				# bones with pad to max, added as RELATIVE
				for b,w in v.influences:
					ad.append(oldbone2newbone[b])
				for i in range(ni,maxinfluence):
					ad.append(0)
				if m.numtexcoords > 0:
					ad.append(v.texcoords[0][0])
					ad.append(v.texcoords[0][1])
				else:
					ad.append(0)
					ad.append(0)
			fd = []
			for f in m.faces:
				fd.append(f[0])
				fd.append(f[1])
				fd.append(f[2])
			md["vertices"] = numpy.array(ad,dtype="float32")
			md["faces"] = numpy.array(fd,dtype="int32")
			md["name"] = m.name
			md["numvertices"] = len(m.vertices)
			md["material"] = m.material
	 		md["stride"] = stride
			md["numinfluences"] = maxinfluence
			md["numtexcoords"] = 1
			md["bones"] = bones
			md["layout"] = ["pos","norm","weights","rel_bones","texcoords"]
			print "dumping",len(ad),"vertexdata",len(ad)/len(m.vertices),"faces:",len(fd)
			dd.append(md)
		#cPickle.dump(dd,open(meshfilename+".pik","wb"),2)
			# build array of all mesh information using standard layout

			# append this mesh to dd
		# store dd

if __name__ == "__main__":
	import sys
	import os

	if len(sys.argv) == 1 or len(sys.argv) > 3:
		print "makejson xcal.xsf [xcal.xmf]"
		sys.exit(0)

	fm = sys.argv[1]
	ext = os.path.splitext(fm)[1]
	if ext.lower() != ".xsf":
		print "not skeleton extension XSF"
		sys.exit(0)

	if len(sys.argv) < 3
		fm2 = os.path.splitext(fm)[0] + ".xmf"
	else:
		fm2 = sys.argv[2]
	ext2 = os.path.splitext(fm2)[1]
	if ext2.lower() != ".xmf":
		print "not mesh extension XMF"
		sys.exit(0)

	ojs = open(os.path.splitext(fm2)[0] + ".json","wb")
	obin = open(os.path.splitext(fm2)[0] + ".bin","wb")

	pa = xcal3d.SkelParser()
	s = pa.load(open(fm,"rb"))

	print "parsing mesh",fm2
	pa = xcal3d.ModelParser()
	sm = pa.load(open(fm2,"rb"))

	o = skel2dic(s)
	o = mesh2dicbin(sm,s,obin)
	json.dump(o,ojs)

