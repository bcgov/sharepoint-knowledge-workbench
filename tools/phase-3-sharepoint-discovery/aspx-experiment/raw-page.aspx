<%@ Page Language="C#" %>
<html>
<head><title>TEST-DO-NOT-USE raw aspx probe</title></head>
<body>
<h2 id="initiate-a-file">INITIATE A FILE</h2>
<p>Specific mandatory data must be entered before a new file can be
saved.</p>
<p>CEIS will check that the following details have been entered:</p>
<ul>
<li><p>File Details</p></li>
<li><p>Party and Role (at least one party and role)</p></li>
<li><p>Initiating Document</p></li>
</ul>
<p>If you abandon the Initiate File sequence without having entered the
above minimum details, this warning message will appear:</p>
<p><img src="https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV/SiteAssets/TEST-DO-NOT-USE-aspx-experiment/image17.gif" />If you select "Yes", the file will
be deleted from the database and all details must be entered again from
the beginning. If you select "No", the screen stays open so you can
continue initiating the file.</p>
<h3 id="how-to-initiate-a-file">How to Initiate a File</h3>
<p><img src="https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV/SiteAssets/TEST-DO-NOT-USE-aspx-experiment/image18.png" />The first step in initiating a file
is to record the file identification details.</p>
<p>NOTE - All the fields in the File Identification screen are
mandatory</p>
<p>NOTE – The Date opened should never be AFTER the filed date of the
initiating document. They should be the same day. The only exception to
that rule is file amalgamation and the initiating document on the
amalgamated file will be different that the new file.</p>
<ol type="1">
<li><p><strong>Court File Number</strong>: The file number that
corresponds to the physical file jacket in your registry. This field
uniquely identifies a file across the province. (At this time, exactly
how new files are to be numbered is left to the discretion of individual
regions.)</p></li>
<li><p><strong>Level</strong>: The level of court: Supreme (S) or
Provincial (P).</p></li>
<li><p><strong>Class</strong>: This is the file type.</p></li>
</ol>
<p>When initiating a Provincial Court civil file, the following classes
must be used:</p>
<table style="width:97%;">
<colgroup>
<col style="width: 5%" />
<col style="width: 39%" />
<col style="width: 5%" />
<col style="width: 5%" />
<col style="width: 43%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">C</th>
<th style="text-align: left;">Small Claims</th>
<th></th>
<th style="text-align: left;">F</th>
<th style="text-align: left;">Family</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">M</td>
<td style="text-align: left;">Motor Vehicle Accidents</td>
<td></td>
<td style="text-align: left;">L</td>
<td style="text-align: left;">Enforcement/Legislated Statutes</td>
</tr>
</tbody>
</table>
<p>NOTE - Class "D" is the old divorce class, so it should not be used
for any new family/divorce files. However, it's referenced in the
documentation because you'll still see your old files in CEIS</p>
<table style="width:97%;">
<colgroup>
<col style="width: 4%" />
<col style="width: 35%" />
<col style="width: 4%" />
<col style="width: 20%" />
<col style="width: 32%" />
</colgroup>
<thead>
<tr>
<th>B</th>
<th>Bankruptcy and Insolvency</th>
<th></th>
<th>N</th>
<th>Adoption</th>
</tr>
</thead>
<tbody>
<tr>
<td>E</td>
<td>Family Law Proceeding</td>
<td></td>
<td>P</td>
<td>Probate and Administration</td>
</tr>
<tr>
<td>H</td>
<td>Foreclosure</td>
<td></td>
<td>S</td>
<td>Supreme Civil General</td>
</tr>
<tr>
<td>L</td>
<td>Enforcement/Legislated Statutes</td>
<td></td>
<td>V</td>
<td>Caveat</td>
</tr>
<tr>
<td>M</td>
<td>Motor Vehicle Accidents</td>
<td></td>
<td colspan="2"></td>
</tr>
</tbody>
</table>
<ol start="4" type="1">
<li><p><strong>Location</strong>: The default location is entered
automatically, but you can select another location if required.</p></li>
<li><p><strong>SAVE</strong>: It's important to note that once you've
filled in the <em>File Identification</em> details, you'll be using the
<strong>Maintain File</strong> screens to enter the rest of the data and
complete the file initiation. These are the exact same screens used for
working with existing files.</p></li>
</ol>
<p>NOTE - When initiating a new Provincial or Supreme Court civil file
in CEIS, use numeric values only. CEIS does not accept alpha characters
in the File Number field for new files.</p>
<h3 id="re-initiating-old-or-destroyed-files">Re-Initiating Old or
Destroyed Files</h3>
<p>In the event you find yourself in a circumstance where a file that
was properly destroyed after 25+ years and is not in CEIS but is being
resurrected and has an upcoming hearing date in a court location. How
should you manage this?</p>
<p>Although there are no real statistical requirements, we recommend
initiating the file under the original file number. Although the
physical file has been destroyed, once a 'case' has a number it should
keep it wherever possible, providing it's still in the same level and
class.</p>
<p>In the File Details Comment section, fill in the detailed that this
file is being resurrected and was originally opened in DayMonthYear.</p>
<p>The purpose is to have a full story of the file within the file, and
also as this is new action on the file, we should have a newer date to
re-set possible retention time frames for this file.</p>
<p>As for the Documents, if we are accepting old documents, enter them
as the date of the new opened date, and in the Document Detail Comments,
place the original filing date if known.</p>
<h3 id="provincial-family-files">Provincial Family Files</h3>
<p>The Provincial Family umbrella has grown with a variety of different
types of family files.</p>
<p>Demystify the changes with this table to ensure you are choosing the
correct type of file:</p>
<table style="width:99%;">
<colgroup>
<col style="width: 3%" />
<col style="width: 12%" />
<col style="width: 22%" />
<col style="width: 33%" />
<col style="width: 27%" />
</colgroup>
<thead>
<tr>
<th></th>
<th colspan="4"><strong>PROVINCIAL FAMILY FILE TYPES</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>TYPE</strong></td>
<td><p><strong>Family Law Act</strong></p>
<p><em>(mom v dad – child support, parenting time, protection orders
etc)</em></p></td>
<td><strong>Child, Family, Community and Services Act</strong>
<em>(Director (government) removes child from guardian due to safety
concerns)</em></td>
<td><strong>Indigenous Law Files</strong> <em>(one or more disputes on
who has jurisdiction of a child who has been removed by the Director,
the Director or Indigenous community who has filed a dispute)</em></td>
<td><strong>Cowichan Files  </strong>(The Chief Executive Officer who is
in need of the courts assistance with a family/child who is under the
care of the Cowichan Law)</td>
</tr>
<tr>
<td><strong>ACT</strong></td>
<td>Family Law Act (FLA)</td>
<td>CFCSA</td>
<td><p>Splatsin Law</p>
<p>Sts’ailes Law</p>
<p>Gwa’sala-’Nakwaxda’wx Law</p>
<p>Cowichan Law</p>
<p>Huu-ay-aht Law</p>
<p>Tsilhqot’in Law</p></td>
<td>Snuw'uy'ulhtst tu Quw'utsun Mustimuhw u' tu Shhw'a'luqwa'a' i'
Smun'eem</td>
</tr>
<tr>
<td><strong>ROLES</strong></td>
<td>Party/Other Party</td>
<td>Applicant (Director)/Child</td>
<td>Applicant/IA (Indigenous Authority)</td>
<td>Applicant (CEO)/Smun’eem</td>
</tr>
<tr>
<td><strong>INITIATING DOC</strong></td>
<td>FLC/AAP/ACMO/ACMW/AEA/AEC/AFCO/AFET/AFET/AGSW etc. 😊</td>
<td>REP/AFO</td>
<td>AOIL/ASCC</td>
<td>APH/AROD</td>
</tr>
<tr>
<td><strong>FLAGS</strong></td>
<td>None</td>
<td>Child Protection (aka CFCSA)</td>
<td>Indigenous Law and Child Protection (aka CFCSA)</td>
<td>Child Protection (aka CFCSA)</td>
</tr>
</tbody>
</table>

</body>
</html>
