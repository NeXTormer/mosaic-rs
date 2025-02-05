import json
import threading
import time
import uuid
from typing import Any

from mosaicrs.pipeline.PipelineIntermediate import PipelineIntermediate
from mosaicrs.pipeline.PipelineStepHandler import PipelineStepHandler
from mosaicrs.pipeline_steps.EmbeddingRerankerStep import EmbeddingRerankerStep
from mosaicrs.pipeline_steps.MosaicDataSource import MosaicDataSource
from mosaicrs.pipeline_steps.PipelineStep import PipelineStep
from mosaicrs.pipeline_steps.DocumentSummarizerStep import DocumentSummarizerStep
from mosaicrs.pipeline_steps.ResultsSummarizerStep import ResultsSummarizerStep

pipeline_steps_mapping = {
    "mosaic_datasource": MosaicDataSource,
    "llm_summarizer": DocumentSummarizerStep,
    "embedding_reranker": EmbeddingRerankerStep,
    "all_results_summarizer": ResultsSummarizerStep
}

class PipelineTask:
    def __init__(self, pipeline):
        self.start_time = None
        self.end_time = None
        self.pipeline = pipeline
        self.thread_args = {
            'current_step': '',
            'pipeline_step_handler': PipelineStepHandler(),
            'pipeline_progress': '0',
            'pipeline_percentage': 0,
            'result': None,
        }

        self.uuid = uuid.uuid4().hex
        self.thread = threading.Thread(target=_run_pipeline, args=(self.pipeline, self.thread_args))


    def start(self):
        self.start_time = time.time()
        self.thread.start()


    def cancel(self):
        self.thread_args['pipeline_step_handler'].should_cancel = True
        self.thread.join()


    def get_status(self) -> dict[str, Any]:
        data =  {
            'current_step': self.thread_args['current_step'],
            'pipeline_progress': self.thread_args['pipeline_progress'],
            'pipeline_percentage': self.thread_args['pipeline_percentage'],
            'result': None,
            'metadata': None,
        }
        data.update(self.thread_args['pipeline_step_handler'].get_progress())

        if self.thread_args['result'] is not None:
            data['result'] = self.thread_args['result'].documents.to_json(orient='records')
            data['metadata'] = self.thread_args['result'].metadata.to_json(orient='records')


        return data


def _run_pipeline(pipeline, args):
    steps = pipeline['pipeline']
    query = ''
    parameters = {}

    if 'query' in steps:
        query = steps['query']
        del steps['query']

    if 'parameters' in steps:
        parameters = steps['parameters']
        del steps['parameters']

    current_step_index = 0
    total_steps = len(steps)

    args['current_step'] = 'Starting...'
    args['step_progress'] = ''
    args['step_percentage'] = 0
    args['pipeline_progress'] = str(current_step_index) + '/' + str(total_steps)
    args['pipeline_percentage'] = 0
    args['result'] = None

    print("Running pipeline. Query: " + query)

    keys = sorted([int(x) for x in steps.keys()])

    data = PipelineIntermediate(query=query, arguments=parameters)

    for key in keys:
        step_id = steps[str(key)]['id']
        step_parameters = steps[str(key)]['parameters']

        print("Processing " + step_id)

        step = _get_class_from_id_and_parameters(step_id, step_parameters)


        args['current_step'] = step.get_name()
        args['pipeline_progress'] = str(current_step_index) + '/' + str(total_steps)
        args['pipeline_percentage'] = current_step_index / total_steps

        args['pipeline_step_handler'].reset()
        data = step.transform(data, handler=args['pipeline_step_handler'])
        current_step_index += 1

    args['pipeline_progress'] = str(current_step_index) + '/' + str(total_steps)
    args['step_percentage'] = 1
    args['pipeline_percentage'] = 1

    args['result'] = data


def _get_class_from_id_and_parameters(step_id: str, step_parameters: dict) -> PipelineStep:
    cls = pipeline_steps_mapping[step_id]

    instance = cls(**step_parameters)

    return instance

def get_pipeline_info():
    all_steps = {}
    for k, v in pipeline_steps_mapping.items():
        info = v.get_info()

        all_steps[k] = info

    return json.dumps(all_steps)

