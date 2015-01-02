from trackhub import Track, default_hub, default_assembly_hub
from trackhub.upload import upload_hub, upload_track, upload_file
import os

hub, genomes_file, genome, trackdb, groups = default_assembly_hub(
    hub_name="myhub",
    genome="dm3",
    twoBitPath='chr2L.2bit',
    short_label="example hub",
    long_label="My example hub",
    email="none@example.com")

# publicly accessible hub URL
hub.url = "http://helix.nih.gov/~dalerr/test/test_hub.txt"

# hub's location on remote host, for use with rsync
hub.remote_fn = "/data/dalerr/datashare/test/test_hub.txt"

# Make tracks for all bigWigs in current dir
import glob, os
for fn in glob.glob('test/data/*.bw'):
    label = os.path.basename(fn).replace('.bedgraph.bw', '')

    # Parameters are checked for valid values, see 
    # http://genome.ucsc.edu/goldenPath/help/trackDb/trackDbHub.html
    # for what's available
    track = Track(
        name=label,
        short_label=label,
        long_label=label,
        autoScale='off',
        local_fn=fn,
        tracktype='bigWig',
        )
    trackdb.add_tracks(track)

# Demonstrate some post-creation adjustments...here, just make control
# samples gray
for track in trackdb.tracks:
    if 'control' in track.name:
        track.add_params(color="100,100,100")

# Render the hub to text files
hub.render()

# Upload the hub files and all the bigwig files using rsync.
kwargs = dict(host='helix.nih.gov', user='dalerr')
upload_file(local_fn=genome.twoBitPath, remote_fn=genome.twoBitPath_remote, **kwargs)
upload_hub(hub=hub, **kwargs)
for track, level in hub.leaves(Track):
    upload_track(track=track, **kwargs)


print hub.url
