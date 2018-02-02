#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import gpxpy
import os

class GPXMerge:

  def __init__(self, **kwargs):
    self.directory = os.path.abspath(kwargs['input'])
    # Use output path if provided
    if kwargs['output']:
      self.out_path = os.path.abspath(kwargs['output'])
    # Else use "[current_directory]/[input basename]_merged.gpx""
    else:
      filename = os.path.basename(kwargs['input']) + '_merged.gpx'
      self.out_path = os.path.abspath(filename)
    self.skip_intveral = int(kwargs['skip_interval'])
    self.tracks = []
    
  def merge(self):
    """ Populate and update self.trackpoints with the merged and sorted trackpoints """
    self.populate_trackpoints()

  def writeout(self):
    """ Write out merged GPS to disk """
    gpx = self.to_gpx()
    with open(self.out_path, 'w') as f:
      f.write(gpx)

  def populate_trackpoints(self):
    """ Populate self.trackpoints by loading all GPX trackpoints within directory """
    for filename in os.listdir(self.directory):
      if os.path.splitext(filename)[1] == '.gpx':
        file_path = os.path.abspath(os.path.join(self.directory, filename))
        with open(file_path, 'r') as f:
          gpx = gpxpy.parse(f)
          # Iterate each track
          for trk in gpx.tracks:
            track = [] # list of processed trksegs
            # Iterate each segment within track
            for trkseg in trk.segments:
              # 1. Extract out trkpt at given intervals
              track_segment = trkseg.points[::self.skip_intveral]                 
              # 2. Remove trkpts without timestamp
              track_segment = filter(lambda trkpt: trkpt.time is not None, track_segment)
              # 3. Sort trkpts chronologically
              track_segment.sort(key=lambda trkpt: trkpt.time)
              # 4. Append to track the processed trkseg of trkpts
              track.append(track_segment)
            # Append to tracks the processed track
            self.tracks.append(track)
  
  def to_gpx(self):
    """ Convert a list of tacks into a GPX file """
    gpx = gpxpy.gpx.GPX()
    # Build tracks
    for track in self.tracks:
      trk = gpxpy.gpx.GPXTrack()
      # Build track segments
      for track_segment in track:
        trkseg = gpxpy.gpx.GPXTrackSegment()
        trkseg.points = track_segment
        trk.segments.append(trkseg)
      gpx.tracks.append(trk)
    return gpx.to_xml()

def main():
  parser = argparse.ArgumentParser(
    description="Merges all trackpoints in GPX files within a directory and write out merged GPX",
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument('--input', '-i', help='Input directory containing GPX files')
  parser.add_argument('--output', '-o', help='Output GPX file with merged trackpoints')
  parser.add_argument('--skip-interval', '-s', default=1, help='The interval in which the trackpoints within are ignored')
  args = parser.parse_args()

  gpx_merger = GPXMerge(**vars(args))
  gpx_merger.merge()
  gpx_merger.writeout()

if __name__ == '__main__':
  main()
