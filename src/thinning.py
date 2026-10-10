"""Visible-berry decision support; no hidden-berry estimation or robot actuation."""
from dataclasses import dataclass, asdict
import numpy as np

@dataclass
class Decision:
    id: int
    box: list
    confidence: float
    relative_diameter: float
    action: str
    reason: str

def decide(boxes, scores, size_ratio=0.70, visible_target=None):
    """Small means sqrt(box area) < ratio * median sqrt(box area).

    `visible_target` is only a user-selected target for a covered ROI, never a
    full-bunch agronomic recommendation inferred from a single photograph.
    """
    if not 0<size_ratio<=1: raise ValueError('size_ratio must be in (0, 1]')
    if visible_target is not None and (isinstance(visible_target,bool) or int(visible_target)!=visible_target or visible_target<0):
        raise ValueError('visible_target must be a non-negative integer')
    b=np.asarray(boxes,dtype=float).reshape(-1,4);s=np.asarray(scores,dtype=float)
    if len(s)!=len(b) or not np.isfinite(b).all() or not np.isfinite(s).all() or (s<0).any() or (s>1).any():raise ValueError('invalid detections')
    if not len(b):return dict(visible_count=0,remove_count=0,keep_count=0,decisions=[])
    wh=b[:,2:]-b[:,:2]
    if (wh<=0).any():raise ValueError('boxes must have positive dimensions')
    diameter=np.sqrt(wh.prod(axis=1));relative=diameter/np.median(diameter)
    remove=relative<size_ratio;reasons=np.where(remove,'relative_small','keep').astype(object)
    if visible_target is not None and (~remove).sum()>visible_target:
        # Remove the smaller member in the closest normalized pair; recompute after each removal.
        centers=(b[:,:2]+b[:,2:])/2
        while (~remove).sum()>visible_target:
            idx=np.flatnonzero(~remove)
            if len(idx)==1:chosen=idx[0]
            else:
                dist=np.linalg.norm(centers[idx,None]-centers[None,idx],axis=-1)
                dist/=np.maximum((diameter[idx,None]+diameter[None,idx])/2,1e-9)
                np.fill_diagonal(dist,np.inf);a,c=np.unravel_index(dist.argmin(),dist.shape)
                pair=[idx[a],idx[c]];chosen=min(pair,key=lambda j:(diameter[j],s[j],j))
            remove[chosen]=True;reasons[chosen]='crowding_target'
    rows=[asdict(Decision(i+1,box.tolist(),float(s[i]),float(relative[i]),'remove' if remove[i] else 'keep',str(reasons[i]))) for i,box in enumerate(b)]
    return dict(visible_count=len(b),remove_count=int(remove.sum()),keep_count=int((~remove).sum()),size_ratio=size_ratio,visible_target=visible_target,decisions=rows)
