/*
 *  Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
 *  Copyright 2018 Marco Martin <mart@kde.org>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.

 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.

 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.9
import QtQuick.Layouts 1.4
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.3
import org.kde.kirigami 2.8 as Kirigami
import Mycroft 1.0 as Mycroft


Mycroft.Delegate {
    id: delegate
    fillWidth: true
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0

    skillBackgroundSource: "https://source.unsplash.com/1920x1080/?+music"

    Keys.onBackPressed: {
        parent.parent.parent.currentIndex++
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }

    contentItem: ColumnLayout {
        id: colLay1

        Component {
            id: homeCat
            CategoryBoxHomeView {
                id: homeCatView
            }
        }

        Kirigami.Heading {
            id: watchItemList
            text: "Skills"
            level: 2
        }

        Kirigami.Separator {
            id: sept2
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            z: 100
        }

        StackView {
            id: categoryLayout
            Layout.fillWidth: true
            Layout.fillHeight: true

            Component.onCompleted: {
                categoryLayout.push(homeCat)
            }
        }
    }
}

