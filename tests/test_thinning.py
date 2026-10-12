import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from thinning import decide
class ThinningTests(unittest.TestCase):
 def test_monotone_size_threshold(self):
  boxes=[[i*20,0,i*20+s,s] for i,s in enumerate([3,5,6,7,9,10,11,14])]
  counts=[decide(boxes,[.9]*len(boxes),size_ratio=t)['remove_count'] for t in [.3,.5,.6,.7,.8,.9,1.0]]
  self.assertEqual(counts,sorted(counts))
 def test_scale_schema_and_conservation(self):
  r=decide([[0,0,10,10],[20,0,24,4]],[.9,.8])
  self.assertEqual(r['visible_count'],r['keep_count']+r['remove_count'])
  self.assertIn('relative_scale',r['decisions'][0]);self.assertNotIn('relative_diameter',r['decisions'][0])
 def test_empty(self):self.assertEqual(decide([],[])['keep_count'],0)
 def test_small_threshold(self):
  r=decide([[0,0,10,10],[20,0,30,10],[40,0,44,4]],[.9]*3)
  self.assertEqual(r['remove_count'],1);self.assertEqual(r['decisions'][2]['reason'],'relative_small')
 def test_scale_invariance(self):
  b=[[0,0,10,10],[20,0,30,10],[40,0,44,4]]
  a=decide(b,[1]*3);c=decide([[v*10 for v in x] for x in b],[1]*3)
  self.assertEqual([d['action'] for d in a['decisions']],[d['action'] for d in c['decisions']])
 def test_target_never_invents_berries(self):
  r=decide([[0,0,10,10]],[.9],visible_target=50);self.assertEqual(r['keep_count'],1)
 def test_zero_target(self):self.assertEqual(decide([[0,0,10,10]],[.9],visible_target=0)['keep_count'],0)
 def test_invalid(self):
  for kw in [dict(size_ratio=0),dict(visible_target=-1),dict(visible_target=1.5)]:
   with self.assertRaises(ValueError):decide([],[],**kw)
  with self.assertRaises(ValueError):decide([[1,1,0,0]],[.5])
if __name__=='__main__':unittest.main()
