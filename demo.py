# -*- coding: utf-8 -*-
"""
Created on 2022/1/24 20:55
@author  : GMT
"""
import os
from src.evaluation import Evaluator
from src.log import logger
import motmetrics as mm

def write_results(filename, results, data_type):
    if data_type == 'mot':
        save_format = '{frame},{id},{x1},{y1},{w},{h},1,-1,-1,-1\n'
    elif data_type == 'kitti':
        save_format = '{frame} {id} pedestrian 0 0 -10 {x1} {y1} {x2} {y2} -10 -10 -10 -1000 -1000 -1000 -10\n'
    else:
        raise ValueError(data_type)

    with open(filename, 'w') as f:
        for frame_id, tlwhs, track_ids in results:
            if data_type == 'kitti':
                frame_id -= 1
            for tlwh, track_id in zip(tlwhs, track_ids):
                if track_id < 0:
                    continue
                x1, y1, w, h = tlwh
                x2, y2 = x1 + w, y1 + h
                line = save_format.format(frame=frame_id, id=track_id, x1=x1, y1=y1, x2=x2, y2=y2, w=w, h=h)
                f.write(line)
    logger.info('save results to {}'.format(filename))


def eval_frames(path, results, seqs):
    accs = []
    data_type = 'mot'
    exp_name = "demo"
    seqs = set()
    seqs.add(os.path.basename(path.split('/')[-1]))
    result_filename = path.replace('.mp4' ,"_mot16_pred.txt")
    write_results(result_filename, results, data_type)
    evaluator = Evaluator(result_filename, seqs, data_type)
    accs.append(evaluator.eval_file(result_filename))
    metrics = mm.metrics.motchallenge_metrics
    mh = mm.metrics.create()
    summary = Evaluator.get_summary(accs, seqs, metrics)
    strsummary = mm.io.render_summary(
        summary,
        formatters=mh.formatters,
        namemap=mm.io.motchallenge_metric_names
    )
    print(strsummary)
    Evaluator.save_summary(summary, path.replace('.mp4' ,'summary_{}.xlsx'.format(exp_name)))


if __name__ == '__main__':
    path = "your videos path"
    results = [] # results.append((frame_idx - 1, online_tlwhs, online_ids))
    seqs = [pathi for pathi in os.listdirs(path)]
    eval_frames(path, results, seqs)
