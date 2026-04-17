**UCIe**** ****PHY **

Databook

Copyright Notice and Proprietary Information Notice

Copyright © 2025 Synopsys, Inc. All rights reserved. This software and documentation contain confidential and proprietary information that is the property of Synopsys, Inc. The software and documentation are furnished under a license agreement and may be used or copied only in accordance with the terms of the license agreement. No part of the software and documentation may be reproduced, transmitted, or translated, in any form or by any means, electronic, mechanical, manual, optical, or otherwise, without prior written permission of Synopsys, Inc., or as expressly provided by the license agreement.

Destination Control Statement

All technical data contained in this publication is subject to the export control laws of the United States of America. Disclosure to nationals of other countries contrary to United States law is prohibited. It is the reader's responsibility to determine the applicable regulations and to comply with them.

Disclaimer

SYNOPSYS, INC., AND ITS LICENSORS MAKE NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD TO THIS MATERIAL, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

Trademarks

Synopsys and certain Synopsys product names are trademarks of Synopsys, as set forth at

All other product or company names may be trademarks of their respective owners.

Synopsys, Inc.690 E. Middlefield RoadMountain View, CA 94043

# Revision History

| Date | Owner | Revision | Description |
| --- | --- | --- | --- |
| **Jan 26, 2026** | Tri Vo | 0.3 | Update Analog connection section: x32 custom PHY config with separating vbg and vreg_ato |
| **Oct 28, 2025** | Tri Vo | 0.2 | Add SIM scan connection |
| **Sep**** ****21****, 202****5** | Tri Vo | 0.1 | Initial version for pin list and functional diagram only |

# Introduction

This document provides the analog macro integration guidelines for RTL implementation.

# Analog Signal Connection

## Introduction

This section describes the rule for analog connection from MMCTRL to DW.

## Bandgap Voltage (Vbg) And Current Referent (Iref*)

### General rule

- DW index is labeled from 0 to max and from LEFT to RIGHT.
- There are totally 17 Irefs from Bandgap macro. 16 Irefs will be used for MMx. 1 Iref is for POR connected internally inside MMCTRL.
- 8 Irefs for MMx on LEFT half of PHY. Always labeled from LEF to RIGHT, start by Iref[0] and end by Iref[7].
- 8 Irefs for MMx on RIGHT half of PHY. Always labeled from LEF to RIGHT, start by Iref[8] and end by Iref[15].
- For the case UCIe-S x32, the rule is similar but each MMx needs two Irefs.
- For EW PHY orientation, DW index will be labeled from 0 to max and from the BOTTOM to the TOP. Iref connection rule is similar but change to BOTTOM to TOP.
- Bandgap voltage is shared for all MMx.
### Sample

#### UCIe-A x64/x32 and UCIe-S x16

#### UCIe-S x32

- Standard PHY configuration
Custom PHY configuration

## Voltage Regulator Analog Testout

Analog testout of voltage regulator of all MMx is connected together and then connected to Analog Testout in MMCTRL.

When doing the test, one and only one MMx is selected.

# Near-Side Loopback

## Introduction

In near-side loopback mode, the loopback data output of two adjacent IO are compared within IO or in DW PUB.

This section describes how to select a pair of IO so that we can minimize the impact of clock skew.

## Transmitter

### UCIe-A

For TXCKP, TXCKN, TXTRK and TXCKRD, the loopback data output is compared with the fixed pattern during loopback training.

### UCIe-S

For TXCKP, TXCKN and TXTRK, the loopback data output is compared with the fixed pattern during loopback training.

For TXVLD, its loopback data output is compared with TXDATA13. The recommended connection is shown in the diagram below.

## Receiver

### UCIe-A

For clock and track receiver, a custom connection from TX to RX is implemented:

- TXCKP RXCKP
- TXCKN RXCKN
- TXTRK RXTRK
- TXCKRD TXCKRX
### UCIe-S

For clock and track receiver, a custom connection from TX to RX is implemented:

- TXCKP RXCKP
- TXCKN RXCKN
- TXTRK RXTRK
# Signal Integrity Monitor Scan Connection

This section describes the SIM scan connection of mainband receivers. In DW level, the scan input/output of each receiver is connected into a chain. This chain serves two purposes: DFT scan test and Collect data mode when SIM in mission mode.

The input and output of scan chain is connected to DW PUB logic.

## UCIe-A

### X64 Configuration

Figure 41 SIM scan connection of UCIe-A x64 configuration

### UCIe-A x32

Figure 42 SIM scan connection of UCIe-A x32 configuration

## UCIe-S

### X16 Configuration

Figure 43 SIM scan connection of UCIe-S x16 configuration

### X32 Configuration

The scan order is the same as x16 configuration, but there are two scan chain: one for first x16 and the second for another x16.
