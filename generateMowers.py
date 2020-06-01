# needs pip install HiYaPyCo
import hiyapyco
import re
from collections import OrderedDict

# describe your mower names
mower_names = ['vanvoor','vanachter']

##### the generator script #####
# generate packages file
package_file_path = 'packages/landroid.yaml'
package_file_content_begin_string = '# Recorder #######'
target_package_file_path = 'packages/landroids.yaml'
## read original content
package_file = open(package_file_path,'r', encoding="utf8")
package_file_text = package_file.read()
package_file.close()
package_file_content_index = package_file_text.index(package_file_content_begin_string)
package_file_header = package_file_text[:package_file_content_index]
package_file_content = package_file_text[package_file_content_index:]
## write file with all mowers
yamlList = []
for mower in mower_names:
    mower_text = package_file_content
    mower_text = re.sub('_mower_','_', mower_text)
    mower_text = re.sub('landroid_','landroid_{0}_'.format(mower), mower_text)
    mower_text = re.sub('landroid_{0}_cloud'.format(mower),'landroid_cloud', mower_text)
    mower_text = re.sub('alias: Landroid','alias: Landroid {0}'.format(mower), mower_text)
    #remove secrets for now, they will disapear in the future with upgrades from landroid cloud
    mower_text = re.sub('!secret landroid_.*','""', mower_text)
    # fix German to default English
    mower_text = re.sub('Lädt','Charging', mower_text)
    mower_text = re.sub('Entlädt','Discharging', mower_text)
    yamlList.append("## Landroid mower {0} ##\r\n{1}".format(mower, mower_text))
    # add mower name and id
    yamlList.append("""
recorder:
  exclude:
    entities:
    - sensor.landroid_{0}_name
    - sensor.landroid_{0}_id
logbook:
  exclude:
    entities:
    - sensor.landroid_{0}_name
    - sensor.landroid_{0}_id
sensor:
- platform: template
  sensors:
    landroid_{0}_name:
      friendly_name: Mower name
      value_template: "{{ state_attr('sensor.landroid_{0}_status', 'friendly_name')[:-7] }}"
    landroid_id:
      friendly_name: Mower id number
      value_template: "{{ state_attr('sensor.landroid_{0}_status', 'id') }}"
      icon_template: mdi:numeric
    """.format(mower))

merged_yaml = hiyapyco.load(yamlList, method=hiyapyco.METHOD_MERGE)
target_package_file = open(target_package_file_path, 'w', encoding="utf8")
target_package_file.write(package_file_header)
target_package_file.write(hiyapyco.dump(merged_yaml))
target_package_file.close()

# generate lovelace files
## read original content
lovelace_file_path = 'lovelace/card.yaml'
lovelace_file = open(lovelace_file_path,'r', encoding="utf8")
lovelace_file_text = lovelace_file.read()
## generate mower cards
for mower in mower_names:
    target_lovelace_file_path = "lovelace/card_{0}.yaml".format(mower)
    mower_text = lovelace_file_text
    mower_text = re.sub('_mower_','_', mower_text)
    mower_text = re.sub('landroid_','landroid_{0}_'.format(mower), mower_text)
    mower_text = re.sub(r'landroid_{0}(.*).png'.format(mower),r'landroid\1.png', mower_text)
    yaml_card = hiyapyco.load(mower_text, method=hiyapyco.METHOD_SIMPLE)
    # add name, id to info
    for item in yaml_card['cards']:
      if 'card' in item and 'entities' in item['card'] and 'entities' in item['card']['entities'][0]:
        item['card']['entities'][0]['entities'].insert(0, OrderedDict([('entity', 'sensor.landroid_{0}_name'.format(mower))]))
        item['card']['entities'][0]['entities'].insert(1, OrderedDict([('entity', 'sensor.landroid_{0}_id'.format(mower))]))
    # if you have multiple mowers, add mower name at the top of the card
    if len(mower_names) > 1:
        yaml_card['cards'][0]['elements'].append(hiyapyco.load("""
  entity: sensor.landroid_{0}_name
  style:
    color: 'rgb(3, 169, 244)'
    font-size: 200%
    font-weight: bold
    left: 50%
    top: 1%
    transform: translate(-50%, 0%)
  type: state-label""".format(mower)))
    target_lovelace_file = open(target_lovelace_file_path,'w', encoding="utf8")
    target_lovelace_file.write(hiyapyco.dump(yaml_card))
    target_lovelace_file.close()

