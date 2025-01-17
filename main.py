from argparse import ArgumentParser
from yolov8 import YOLOv8

import inotify.adapters
import logging
import sys
import yolov8.watcher as watcher


def main(args):
    arg_parser = ArgumentParser(prog=__file__, add_help=False)
    arg_parser.add_argument('--log-level', default='INFO', help='set log level')
    arg_parser.add_argument('--input-height', default='960', help='set input height for model')
    arg_parser.add_argument('--input-width', default='960', help='set input wisdth for model')
    arg_parser.add_argument('--model-path', default='/mnt/data/models/pvc.onnx', help='set path of the onnx privacy model')
    arg_parser.add_argument('--show-detection', default=False, help='set if we want to draw detections or not')
    arg_parser.add_argument('--unprocessed-framekm-path', default='/mnt/data/unprocessed_framekm', help='set the path for the unprocessed framekm')
    arg_parser.add_argument('--framekm-path', default='/mnt/data/framekm', help='set the path for the processed framekm')
    arg_parser.add_argument('--metadata-path', default='/mnt/data/metadata', help='set the path for the processed framekm metadata')
    arg_parser.add_argument('--ml-metadata-path', default='/mnt/data/ml_metadata', help='set the path for the processed framekm ML metadata')
    arg_parser.add_argument('--model-hash-path', default='/mnt/data/models/pvc.onnx.hash', help='set the path for the hash of the model')
    args, _ = arg_parser.parse_known_args(args)

    try:
        logging.basicConfig(format='[%(process)d] %(levelname)s: %(message)s', level=args.log_level)
    except ValueError:
        logging.error("Invalid log level: {}".format(args.log_level))
        sys.exit(1)
    
    logger = logging.getLogger(__name__)
    logger.info("Log level set: {}"
                .format(logging.getLevelName(logger.getEffectiveLevel())))
    logging.info(f'model {args.model_path} with input height: {args.input_height} input width: {args.input_height} initialized...')

    unprocessed_framekm_path = args.unprocessed_framekm_path
    framekm_path = args.framekm_path
    metadata_path = args.metadata_path
    ml_metadata_path = args.ml_metadata_path

    yolov8_detector = YOLOv8(args.model_path, logger, int(args.input_height), int(args.input_width), args.show_detection, args.model_hash_path, conf_thres=0.2, iou_thres=0.3)
    w = watcher.Watcher(yolov8_detector, framekm_path, metadata_path, ml_metadata_path, logger)
    w.add_watch(unprocessed_framekm_path)

    try:
        logging.info('starting watcher...')
        w.run()
    except inotify.adapters.TerminalEventException as tee:
        logging.info('bye')
    except KeyboardInterrupt as ki:
        logging.info('bye')
    except Exception as e:
        raise e


if __name__ == "__main__":
    main(sys.argv[1:])
