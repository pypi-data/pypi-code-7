#
# Cal3d mesh filter by emanuele ruffaldi
#
# Produces a JSON + Binary
#

import xcal3d
import sys
from array import array
import numpy,json

def skel2dic(o,s):
	bones = []
	for b in s.bones.values():
		bo = dict(id=b.id,pid=b.pid,name=b.name,tx=str(b.tx)[1:-1].strip(),quat=str(b.rot)[1:-1].strip(),localtx=str(b.localtx)[1:-1].strip(),localquat=str(b.localrot)[1:-1].strip())
		bones.append(bo)
	o["bones"] = bones
	return o

def materials2dic(o,mm):
	o["materials"] = []
	for m in mm:
		mp = xcal3d.MaterialParser()
		ma = mp.load(open(m,"rb"))
		md = dict(ambient=str(ma.ambient)[1:-1].strip(),diffuse=str(ma.diffuse)[1:-1].strip(),specular=str(ma.specular)[1:-1].strip(),shininess=ma.shininess)
		mms = []
		print ma.maps
		for xma in ma.maps:
			mms.append(xma)
		md["maps"] = mms
		o["materials"].append(md)
	return o
	
def mesh2dicbin(meshdata,o,obin,maxinfluence=4,maxtransforms=52,maxtexcoords=1):

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

		if True:
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
					for k in range(0,m.numtexcoords):
						ad.append(v.texcoords[k][0])
						ad.append(v.texcoords[k][1])
			fd = []
			for f in m.faces:
				fd.append(f[0])
				fd.append(f[1])
				fd.append(f[2])

			# store veretex data
			ad = array("f",ad)
			voffset = obin.tell()
			vs = ad.tostring()
			obin.write(vs)

			# store face data
			fd = array("i",fd)
			foffset = obin.tell()
			fs = fd.tostring()
			obin.write(fs)

			l = []
			l.append(dict(type="vertex",offset=0,size=3))
			l.append(dict(type="normal",offset=3*4,size=3))
			l.append(dict(type="weights",offset=6*4,size=maxinfluence))
			l.append(dict(type="relbones",offset=6*4+maxinfluence*4,size=maxinfluence))
			if m.numtexcoords:
				l.append(dict(type="texcoords",offset=6*4+maxinfluence*4*2,size=m.numtexcoords*2))

			md["vertices"] = dict(offset=voffset,count=len(m.vertices),bytesize=len(vs),stride=(3+3+maxinfluence*2+m.numtexcoords*2)*4,layout=l,type="float32")
			md["faces"] =  dict(offset=foffset,count=len(m.faces),bytesize=len(fs),stride=3*2,type="int32")
			md["name"] = m.name
			md["material"] = m.material
			md["numinfluences"] = maxinfluence
			md["numtexcoords"] = m.numtexcoords
			md["relbones"] = bones
			print "dumping",len(ad),"vertexdata",len(ad)/len(m.vertices),"faces:",len(fd)
			dd.append(md)
		#cPickle.dump(dd,open(meshfilename+".pik","wb"),2)
			# build array of all mesh information using standard layout

			# append this mesh to dd
		# store dd
	o["mesh"] = dd
	return o

def fixpath(s,basepath):
	n,e = os.path.splitext(s)
	e = e.lower()
	reps = dict(csf="xsf",cmf="xmf",crf="xrf")
	e = "."+reps.get(e[1:],e[1:])
	return os.path.join(basepath,n+e)

if __name__ == "__main__":
	import sys
	import os

	if len(sys.argv) == 1 or len(sys.argv) > 3:
		print "makejson xcal.xsf [xcal.xmf]"
		print "makejson xcal.cfg"
		sys.exit(0)

	fm = sys.argv[1]
	ext = os.path.splitext(fm)[1]
	materials = []
	if ext.lower() == ".cfg":
		print "configmode"
		cp = xcal3d.ConfigParser()
		c = cp.load(open(fm))

		skel = c.values["skeleton"]
		mesh = c.values["mesh"]
		materials = c.materials

		# adjust paths
		basepath,anem = os.path.split(fm)
		skel = fixpath(skel,basepath)
		mesh = fixpath(mesh,basepath)
		materials = [fixpath(m,basepath) for m in materials]
		obase = os.path.splitext(fm)[0]

		fm = skel
		fm2 = mesh

	elif ext.lower() != ".xsf":
		print "not skeleton extension XSF"
		sys.exit(0)
	else:
		obase = os.path.splitext(fm)[0]
		if len(sys.argv) < 3:
			fm2 = os.path.splitext(fm)[0] + ".xmf"
		else:
			fm2 = sys.argv[2]

	ext2 = os.path.splitext(fm2)[1]
	if ext2.lower() != ".xmf":
		print "not mesh extension XMF"
		sys.exit(0)

	ojs = open(obase+ ".json","wb")
	obin = open(obase + ".bin","wb")

	pa = xcal3d.SkelParser()
	s = pa.load(open(fm,"rb"))

	print "parsing mesh",fm2
	pa = xcal3d.ModelParser()
	sm = pa.load(open(fm2,"rb"))

	o = skel2dic({},s)
	if len(materials) > 0:
		o = materials2dic(o,materials)
	o = mesh2dicbin(sm,o,obin)
	json.dump(o,ojs)
	#print o
	
