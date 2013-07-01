# -*- encoding: utf-8 -*-
import simplejson as json
from importlib import import_module

import feed_src

def _load_state():
    with open('feed_state', 'r') as f:
        state = json.load(f)
    return state

def _save_state(states):
    with open('feed_state', 'w') as f:
        json.dump(states, f)

def main(cursor):
    state = _load_state()
    for feed in feed_src.default_feeds:
        if feed['feed_url'] not in state:
            state[feed['feed_url']] = feed

    for url, meta in state.items():
        handler = import_module(meta['handler']).Handler()
        new_articles, new_last = handler.get_articles(url, last=meta['last'])
        bad_count = 0
        for a in new_articles:
            a['source'] = meta['source']
            a['parser_id'] = handler.id
            if not a['cached']:
                bad_count += 1
            # TODO: save_news(a)
        meta['last'] = new_last

    _save_state(state)

if __name__ == '__main__':
    main()
