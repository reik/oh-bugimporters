#!/usr/bin/env python
import argparse
import sys
import json
import mock
import bugimporters.trac

def dict2obj(d):
    class Trivial(object):
        def get_base_url(self):
            return self.base_url
    ret = Trivial()
    for thing in d:
        setattr(ret, thing, d[thing])
    ret.old_trac = False # FIXME, hack
    ret.max_connections = 5 # FIXME, hack
    ret.as_appears_in_distribution = ''# FIXME, hack
    return ret

class FakeReactorManager(object):
    def __init__(self):
        self.running_deferreds = 0 # FIXME: Hack
    def maybe_quit(self, *args, **kwargs): ## FIXME: Hack
        return

def main(raw_arguments):
    parser = argparse.ArgumentParser(description='Simple oh-bugimporters crawl program')

    parser.add_argument('-i', action="store", dest="input")
    parser.add_argument('-o', action="store", dest="output")
    args = parser.parse_args(raw_arguments)

    json_data = json.load(open(args.input))
    objs = []
    for d in json_data:
        objs.append(dict2obj(d))

    for obj in objs:
        bug_data = []
        def generate_bug_transit(bug_data=bug_data):
            def bug_transit(bug):
                bug_data.append(bug)
            return {'get_fresh_urls': lambda *args: {},
                    'update': bug_transit,
                    'delete_by_url': lambda *args: {}}

        bug_importer = bugimporters.trac.SynchronousTracBugImporter(
            obj, FakeReactorManager(),
            data_transits={'bug': generate_bug_transit(),
                           'trac': {
                    'get_bug_times': lambda url: (None, None),
                    'get_timeline_url': mock.Mock(),
                    'update_timeline': mock.Mock()
                    }})
        class StupidQuery(object):
            @staticmethod
            def get_query_url():
                return 'http://twistedmatrix.com/trac/query?format=csv&col=id&col=summary&col=status&col=owner&col=type&col=priority&col=milestone&id=5228&order=priority' # FIXME: Hack
            @staticmethod
            def save(*args, **kwargs):
                pass # FIXME: Hack
        queries = [StupidQuery]
        bug_importer.process_queries(queries)
        print "YAHOO", bug_data

if __name__ == '__main__':
    main(sys.argv[1:])
