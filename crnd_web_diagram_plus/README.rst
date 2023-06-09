Web Diagram Plus
================

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

.. |badge3| image:: https://img.shields.io/badge/powered%20by-yodoo.systems-00a09d.png
    :target: https://yodoo.systems
    
.. |badge5| image:: https://img.shields.io/badge/maintainer-CR&D-purple.png
    :target: https://crnd.pro/

.. |badge6| image:: https://img.shields.io/badge/GitHub-CRnD_Web_Diagram_Plus-green.png
    :target: https://github.com/crnd-inc/crnd-web/tree/11.0/crnd_web_diagram_plus
    

|badge2| |badge5| |badge6|

This is fork of `web_diagram <https://github.com/odoo/odoo/tree/11.0/addons/web_diagram>`__ addon.

Changes:

- Applied `Pull Request <https://github.com/odoo/odoo/pull/18975>`__
- Possible to specify background and foreground colors of nodes (via fields)
- Possible to store node position in database, thus there is no more need
  to rearrange flow manually each time you open diagram.

Usage
'''''

See real example of usage at `Bureaucrat Helpdesk Lite <https://github.com/crnd-inc/bureaucrat-helpdesk-lite/blob/12.0/generic_request/views/request_type_view.xml#L522>`__

Simple example for internal usage:

.. code:: xml

    <record id="some_id" model="ir.ui.view">
        <field name="model">model.name</field>
        <field name="type">diagram_plus</field>
        <field name="arch" type="xml">
            <diagram_plus>
                <node object="name.of.model"
                      bgcolor="from_old_diagram_non_priority"
                      bg_color_field="name_of_field_bg_color"
                      fg_color_field="name_of_field_fg_color"
                      d_position_field="name_of_field_to_store_position">
                </node>
                <arrow object="name.of.model"
                       source="source_field(from)"
                       destination="destination_field(to)"
                       label="['name_of_label_field']">
                </arrow>
            </diagram_plus>
        </field>
    </record>

Launch your own ITSM system in 60 seconds:
''''''''''''''''''''''''''''''''''''''''''

Create your own `Bureaucrat ITSM <https://yodoo.systems/saas/template/bureaucrat-itsm-demo-data-95>`__ database

|badge3| 

Bug Tracker
===========

Bugs are tracked on `https://crnd.pro/requests <https://crnd.pro/requests>`_.
In case of trouble, please report there.


Maintainer
''''''''''
.. image:: https://crnd.pro/web/image/3699/300x140/crnd.png

Our web site: https://crnd.pro/

This module is maintained by the Center of Research & Development company.

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you. 

For any questions `contact us <mailto:info@crnd.pro>`__.
