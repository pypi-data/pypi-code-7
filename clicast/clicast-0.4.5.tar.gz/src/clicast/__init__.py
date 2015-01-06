import os
import sys

from clicast.cast import Cast, CastReader


def check_message(url, msg_filter=None, cache_duration=None, allow_exit=False, raises=False, local_file=None, reset=False, **show_kwargs):
  """
  Check remote url for new messages and display them.

  :param str url: Cast file URL to check
  :param callable msg_filter: Filter messages with callable that accepts message string and alert boolean (True for
                              alert message). It should return the original or an updated message, or None if the
                              message should be ignored.
  :param int cache_duration: Cache messages locally for number of seconds to avoid checking the URL too often.
                             This is useful for response latency sensitive CLI to ensure user's experience
                             isn't compromised. Alternatively, you may want to check messages in a seperate thread.
  :param bool allow_exit: Perform sys.exit(1) if cast requests it.
  :param bool raises: Raise exception for failed to download/parse cast file or such.
                      Recommended to set this to False for production / in non-debug mode.
  :param str local_file: Local file path for the cast file URL. It will be used instead of 'url' if exists.
                         This is primarily used for testing / in development.
  :param bool reset: Reset read messages. All messages will be displayed again like the user runs this for the first
                     time
  :param dict show_kwargs: kwargs to be passed to :meth:`clicast.CastReader.show_messages`
  """

  try:
    if local_file and os.path.exists(local_file):
      cast = Cast.from_content(local_file, msg_filter)
    else:
      cast = Cast.from_content(url, msg_filter, cache_duration)

    if reset:
      CastReader.reset()

    reader = CastReader(cast)
    reader.show_messages(**show_kwargs)

    if allow_exit and cast.alert_exit:
      sys.exit(1)
  except Exception:
    if raises:
      raise
