# -*- coding: utf8 -*-

from ckan.logic import get_action, ValidationError

import itertools

import click

from ckan.lib.cli import (
    load_config,
    paster_click_group,
    click_config_option,
)


def package_generator(query, page_size, context={'ignore_auth': True}, dataset_type='dataset'):
    package_search = get_action('package_search')

    # Loop through all items. Each page has {page_size} items.
    # Stop iteration when all items have been looped.
    for index in itertools.count(start=0, step=page_size):
        data_dict = {'include_private': True, 'rows': page_size, 'q': query, 'start': index,
                     'fq': '+dataset_type:' + dataset_type}
        data = package_search(context, data_dict)
        packages = data.get('results', [])
        for package in packages:
            yield package

        # Stop iteration all query results have been looped through
        if data["count"] < (index + page_size):
            return


def apply_patches(package_patches, resource_patches):
    if not package_patches and not resource_patches:
        print 'No patches to process.'
    else:
        package_patch = get_action('package_patch')
        resource_patch = get_action('resource_patch')
        context = {'ignore_auth': True}
        for patch in package_patches:
            try:
                package_patch(context, patch)
            except ValidationError as e:
                print "Migration failed for package %s reason:" % patch['id']
                print e
        for patch in resource_patches:
            try:
                resource_patch(context, patch)
            except ValidationError as e:
                print "Migration failed for resource %s, reason" % patch['id']
                print e


sixodp_showcase_group = paster_click_group(
    summary=u'Showcase related commands.'
)


@sixodp_showcase_group.command(
    u'migrate_title_to_title_translated',
    help=u'Migrates old schema title to the new multi-lang title'
)
@click_config_option
@click.option(u'--dryrun', is_flag=True)
@click.pass_context
def migrate_title_to_title_translated(ctx, config, dryrun):
    load_config(config or ctx.obj['config'])

    showcase_patches = []

    for old_showcase_dict in package_generator('*:*', 1000, dataset_type='showcase'):

        if 'title_translated' in old_showcase_dict:
            continue

        title = old_showcase_dict.get('title')

        patch = {
            'id': old_showcase_dict['id'],
            'title_translated': {
                'fi': title
            }
        }

        showcase_patches.append(patch)

    if dryrun:
        print '\n'.join('%s' % p for p in showcase_patches)
    else:
        # No resource patches so empty parameter is passed
        apply_patches(showcase_patches, [])