<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">  
	<xsl:output method="html" omit-xml-declaration="yes" indent="yes"/>
	<xsl:variable name="server" select="/*/@server"/>
	<xsl:variable name="debug" select="/*/@debug"/>
	<xsl:variable name="logged" select="/*/@logged"/>
	<xsl:variable name="authorized" select="/*/@authorized"/>
	<xsl:template match="/">
		<html>
			<head>
				<xsl:call-template name="head"/>
			</head>
			<body style="padding:1ex">
				<xsl:call-template name="header"/>
				<div><b><xsl:value-of select="name(.)"/><xsl:text> </xsl:text><i><xsl:value-of select="translate(/*/@latname, '_', ' ')"/></i></b>
					[<a target="edit" href="/names/edit/name/{/*/@pnid}/">edit</a>]
					<xsl:if test="*[1]/pub_note">
						<xsl:for-each select="*[1]">
							<xsl:call-template name="public_notes"/>
						</xsl:for-each>
					</xsl:if>
					<xsl:for-each select="/*/*[not (name() = 'pub_note') and not (name() = 'annotation') and not (name() = 'note')]">
						<xsl:call-template name="process_taxon"/>
					</xsl:for-each>
				</div>
				<br/>
				<hr/>
				Generated: <i><xsl:value-of select="/*[1]/@generated"/></i>
				<br/>
			</body>
		</html>
	</xsl:template>

	<xsl:template name="public_notes">
<!--		<div>
			<b>Notes</b>: <xsl:copy-of select="pub_note/*|pub_note/text()"/>
		</div>
-->
	</xsl:template>
	
	
	<xsl:template name="header">
        <table bgcolor="#8B0000" border="0" width="100%" cellspacing="0" style="background-color: #8B0000;">
        	<tbody valign="top" style="background-color: #8B0000;">
				<tr>
                    <td bgcolor="#8B0000" nowrap="yes" style="padding-top: 0px; height: 40px; margin-top: 0px; 
	            		vertical-align: middle; text-align:left; background-color: #8B0000; 
	            		font-size: 30pt; color: #F0FFF0;"><img border="0" height="40" alt="" src="/static/images/Salicicola__40.gif"/></td>
	            	<td align="right" bgcolor="#8B0000" nowrap="yes" style="padding-top: 0px; height: 40px; margin-top: 0px; 
	            		vertical-align: middle; text-align:right; background-color: #8B0000; 
	            		font-size: 30pt; color: #F0FFF0;"></td>
				</tr>
			</tbody>
        </table>

<h2 style="max-width:45em"> <!-- max-width:1050px -->
    <span style='white-space: nowrap;'>The Vascular Plants of Massachusetts:</span>
	<xsl:text> </xsl:text>
    <span style='white-space: nowrap;'>Illustrated County Checklist</span>
    <br/>
    <span style="font-size:80%;font-weight:normal">
    	Updated Taxonomy and Distribution (Work in Progress)
    	Flexible Hierarchy. Links provided to families, genera, and, if present, other direct descendants of the genus above species level: 
    	subgenera, sections, and occasionally unplaced taxa.
	</span>
	<br/>
			<div id="container" style="display:none">
			<div style="padding-left:2em;font-weight:normal;font-size:65%;max-width:1100px">
			</div>			
			<div style="padding-top:0.5ex;padding-left:2em;font-weight:normal;font-size:65%;max-width:1100px;">
			</div> 
			</div>
		</h2>
	</xsl:template>
	
	
	<xsl:template name="process_taxon">
	    <xsl:message>process taxon <xsl:value-of select="name()"/> :: <xsl:value-of select="ancestor::genus[1]/@latname"/><xsl:value-of select="ancestor::Genus[1]/@latname"/></xsl:message>
	    <xsl:if test="not(name() = 'annotation')">
	   <!-- <xsl:message> processing <xsl:value-of select="name()"/></xsl:message>-->
		<div style="padding-top:0.5ex;" title="{name()}"> <!--FIXME: cannot use lower-case() in XSLT1 -->
            <xsl:choose>
                <xsl:when test="name() = 'Species'">
                    <xsl:attribute name="id"><xsl:value-of select="ancestor::genus[1]/@latname"/><xsl:value-of select="ancestor::Genus[1]/@latname"/>:<xsl:value-of select="@latname"/></xsl:attribute>
                </xsl:when>
                <!-- FIXME -->
            </xsl:choose>
			<xsl:if test="@counties"><xsl:attribute name="style">padding-top:1ex;</xsl:attribute></xsl:if> <!-- min-height:100px; -->
			<xsl:if test="contains('ABCDEFGHIJKLMNOPQRSTUVWXYZ', substring(@latname, 1, 1))"><xsl:attribute name="id"><xsl:value-of select="translate(@latname, ' ', '')"/></xsl:attribute></xsl:if>
			<xsl:choose>
				<xsl:when test="@nominal"> <!-- i.e., should be var or subsp BUT STILL CAN BE species -->
					<xsl:call-template name="nominal"/>
					<xsl:call-template name="species_level_tail"/>
				</xsl:when>
				<xsl:when test="name() = 'Species'"> <!-- i.e., var or subsp -->
					<xsl:message>processing Species: <xsl:value-of select="ancestor::Genus[1]/@latname"/> <xsl:value-of select="@latname"/></xsl:message>
					<b title="{name()}"><xsl:if test="@pubphotos='0'"><xsl:attribute name="style">color:gray</xsl:attribute></xsl:if> <!-- FIXED all to pubphotos -->
						<i><xsl:value-of select="ancestor::genus[1]/@latname"/><xsl:value-of select="ancestor::Genus[1]/@latname"/> <xsl:text> </xsl:text> <xsl:value-of select="@latname"/></i>
					</b>
					<xsl:text> </xsl:text> <xsl:value-of select="@authors"/>
					<xsl:call-template name="species_level_tail"/>
				</xsl:when>
				<xsl:when test="name() = 'Species_coll'"> <!-- i.e., var or subsp -->
					<b title="{name()}"><xsl:if test="@allphotos='0'"><xsl:attribute name="style">color:gray</xsl:attribute></xsl:if>
						<i><xsl:value-of select="ancestor::genus[1]/@latname"/><xsl:value-of select="ancestor::Genus[1]/@latname"/> <xsl:text> </xsl:text> <xsl:value-of select="@latname"/></i>
					</b>
					<xsl:text> </xsl:text> <xsl:value-of select="@authors"/>
					<xsl:call-template name="species_level_tail"/>
				</xsl:when>
				<xsl:when test="name() = 'Subspecies' or name() = 'Variety' or name() = 'Hybrid' or name() = 'Cultivar'  or name() = 'Forma'">
					<xsl:message>processing infra: <xsl:value-of select="ancestor::Genus[1]/@latname"/> <xsl:value-of select="@latname"/></xsl:message>
					<b title="{name()}">
						<xsl:if test="@allphotos='0'"><xsl:attribute name="style">color:gray</xsl:attribute></xsl:if>
						<i><xsl:value-of select="ancestor::Genus[1]/@latname"/><xsl:value-of select="ancestor::genus[1]/@latname"/></i><xsl:text> </xsl:text>
						<xsl:if test="name() = 'Variety'"> <i><xsl:value-of select="ancestor::Species[1]/@latname"/></i> var. <i><xsl:value-of select="translate(@latname, '_', ' ')"/></i></xsl:if>
						<xsl:if test="name() = 'Subspecies'"> <i><xsl:value-of select="ancestor::Species[1]/@latname"/></i> ssp. <i><xsl:value-of select="translate(@latname, '_', ' ')"/></i></xsl:if>
						<xsl:if test="name() = 'Forma'"> <i><xsl:value-of select="ancestor::Species[1]/@latname"/></i> f. <i><xsl:value-of select="translate(@latname, '_', ' ')"/></i></xsl:if>	
<xsl:if test="name() = 'Cultivar'"> <i><xsl:value-of select="ancestor::Species[1]/@latname"/></i><xsl:text> </xsl:text><xsl:value-of select="translate(@latname, '_', ' ')"/></xsl:if>
<xsl:if test="name() = 'Hybrid'"><!--<i><xsl:value-of select="ancestor::Species[1]/@latname"/></i>--><xsl:text> </xsl:text><i><xsl:value-of select="translate(@latname, '_', ' ')"/></i></xsl:if>


					</b>
					<xsl:text> </xsl:text>
					<xsl:value-of select="@authors"/>
					<xsl:call-template name="species_level_tail"/>
				</xsl:when> 				
				<xsl:otherwise>
					<xsl:choose>
						<xsl:when test="name() = 'Unplaced'">
							Unplaced taxa
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="name(.)"/><xsl:text> </xsl:text>
							<b>
								<xsl:value-of select="translate(@latname, '_', ' ')"/> 
							</b>
						</xsl:otherwise>
					</xsl:choose>
					[<a target="edit" href="/names/edit/name/{@pnid}/">edit</a>] 
					<xsl:if test="pub_note">
						<xsl:call-template name="public_notes"/>
					</xsl:if>
				</xsl:otherwise>
			</xsl:choose>
			<!-- DEBUG -->
			<xsl:if test="$debug">
			<span style="color:red"> [<xsl:value-of select="name()"/> <xsl:if test="@nominal"> nominal=<xsl:value-of select="@nominal"/> </xsl:if>]</span>
			</xsl:if>

			<xsl:for-each select="Synonym">
				<div>
					=
					<i><xsl:value-of select="@latname"/></i>
					<xsl:text> </xsl:text>
					<xsl:value-of select="@authors"/>	
					[<a target="edit" href="/names/edit/name/{@pnid}/">edit</a>]
				</div>
			</xsl:for-each>
			
			<xsl:if test="@counties and string-length(@counties)">
				<xsl:call-template name="details"/>
			</xsl:if>
				
			<xsl:for-each select="*[not (name()='Synonym') and not (contains(name(), 'county')) and not (contains(name(), '_note'))]">
				<xsl:sort select="@latname"/>
				<!-- <xsl:if test="*">  to suppress empty taxa -->
				<xsl:call-template name="process_taxon"/>
				<!--</xsl:if>-->
			</xsl:for-each>
		</div>
	  </xsl:if>
	</xsl:template>
	
	<xsl:template name="species_level_tail">
		[<xsl:value-of select="@colnames"/>]
		[<a target="edit" href="/names/edit/name/{@pnid}/">edit</a>]
		<span title="total {@allphotos} photos">
			<xsl:choose>
				<xsl:when test="not (@pubphotos='0')">
					<!--[<a href="{$server}/photodb/gallery/view/{@pnid}"><xsl:value-of select="@pubphotos"/> published photos</a>]-->
				</xsl:when>
				<xsl:otherwise><!--no photos-->
					<xsl:if test="@allphotos">[<a href="{$server}/photodb/gallery/view/{@pnid}"><xsl:value-of select="@allphotos"/> photos</a>]</xsl:if>
					<xsl:if test="annotation[@kind='photo']">
						[external photos:
						<xsl:for-each select="annotation[@kind='photo']">
							<a target="image" href="{@url}"><xsl:value-of select="position()"/></a><xsl:text> </xsl:text>
						</xsl:for-each>]
					</xsl:if>
				</xsl:otherwise>
			</xsl:choose>
		</span>
		<span>
			[<xsl:if test="annotation"><a target="_blank" href="/admin/names/nameannotation/?q={@pnid}">view</a> / </xsl:if><a target="annotate" href="/admin/names/nameannotation/add/?_changelist_filters=q%3D{@pnid}&amp;plant={@pnid}">add</a>]
			annotation(s) 
		</span>
<!--			<xsl:if test="annotation[@cached and string-length(@cached)]">
			<div style="float:right;">
				<xsl:for-each select="annotation[@cached and string-length(@cached)]">
					<img title="{@cached}" style="max-height:100px;" src="/static/photos/CACHE/{@cached}"/>
					<xsl:text> </xsl:text>
				</xsl:for-each>				
			</div>
			</xsl:if>
-->
	</xsl:template>
	
	<xsl:template name="style">
				  <style type="text/css">
						a {
									text-decoration: none;
						}	
				  .evergreen {
					padding-left: 2em;
				  }
				  li.none {
					list-style-image:none; 
					list-style-type:none; 
					background-color:lightgrey
				  }
				  td.left {
					/* valign="top" */
					width: 20em;
				  }
					.hidden {
					  visibility: visible; /* hidden */
					}
					a {
					font-weight: bold; 
					text-decoration: underline;
					}
					h3 {
					margin-bottom:0;
					padding-bottom:0;
					padding-top:0;
					margin-top:0;
					}
				</style>
	</xsl:template>
	<xsl:template name="head">
			  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
			  <meta name="keywords" content=""/>
			  <title>Massachusetts Photo Gallery</title>
			  <script type="text/javascript" src="/static/scripts/menu.js"><xsl:text> </xsl:text></script>
				<link rel="stylesheet" type="text/css" href="/static/CSS/main.css"/>
				<xsl:call-template name="style"/>
				<style type="text/css">
					body {
						background-color:#F0FFF0;
					}

					div {
						padding-left:1em;
					}
					span.county {
						display: inline-block;width:2em;background-color:#EEEEEE;text-align: center;margin-right:3px;
					}
				</style>

	</xsl:template>
	<xsl:template name="nominal">
						<b title="{name()}">
						<xsl:if test="@allphotos='0'"><xsl:attribute name="style">color:gray</xsl:attribute></xsl:if>
							<i><xsl:value-of select="ancestor::Genus[1]/@latname"/></i><xsl:text> </xsl:text>
							<i><xsl:value-of select="@latname"/></i>
							<xsl:text> </xsl:text><xsl:value-of select="@authors"/> 
							<xsl:text> </xsl:text><xsl:value-of select="@abbr"/><xsl:text> </xsl:text> 
							<i><xsl:value-of select="@latname"/></i>
					</b>
	</xsl:template>
	
	<xsl:template name="details">
				<div style="padding-left:2ex;">
					<div style="padding-left:2ex;"> 
						<table border="0">
							<tbody>
								<tr>
									<td nowrap="true">MA Counties</td>
									<td>	
										<span title="Berkshire" class="county">BE</span>
										<span title="Franklin" class="county">FR</span>
										<span title="Hampshire" class="county">HS</span>
										<span title="Hampden" class="county">HD</span>
										<span title="Worcester" class="county">WO</span>
										<span title="Middlesex" class="county">MI</span>								
										<span title="Essex" class="county">ES</span>
										<span title="Suffolk" class="county">SU</span>
										<span title="Norfolk" class="county">NO</span>
										<span title="Bristol" class="county">BR</span>
										<span title="Plymouth" class="county">PL</span>
										<span title="Barnstable" class="county">BA</span>
										<span title="Dukes" class="county">DU</span>
										<span title="Nantucket" class="county">NA</span>

									</td>
								</tr>
								<tr>
									<td  nowrap="true" title="{@counties}">
										<xsl:choose>
											<xsl:when test="@invasive"><b style="color:red"><xsl:value-of select='@invasive'/></b></xsl:when>
											<xsl:when test="@nonnative">
												<span>
													<xsl:if test="@nonnative='Cultivated'"><xsl:attribute name="style">color:red</xsl:attribute></xsl:if>
													<xsl:if test="@nonnative='Exotic'"><xsl:attribute name="style">color:red</xsl:attribute></xsl:if>
													<xsl:value-of select='@nonnative'/>	
												</span>
											</xsl:when>
											<xsl:when test="@rare">
												[<b style="color:green"><xsl:value-of select='@rare'/></b>]
											</xsl:when>
										</xsl:choose>
										[<xsl:value-of select='@status'/>]
									</td>
									<td>
										<span title="Berkshire" class="county"><xsl:value-of disable-output-escaping="yes" select="county[1]"/></span>
										<span title="Franklin" class="county"><xsl:value-of disable-output-escaping="yes" select="county[2]"/></span>
										<span title="Hampshire" class="county"><xsl:value-of disable-output-escaping="yes" select="county[3]"/></span>
										<span title="Hampden" class="county"><xsl:value-of disable-output-escaping="yes" select="county[4]"/></span>
										<span title="Worcester" class="county"><xsl:value-of disable-output-escaping="yes" select="county[5]"/></span>
										<span title="Middlesex" class="county"><xsl:value-of disable-output-escaping="yes" select="county[6]"/></span>								
										<span title="Essex" class="county"><xsl:value-of disable-output-escaping="yes" select="county[7]"/></span>
										<span title="Suffolk" class="county"><xsl:value-of disable-output-escaping="yes" select="county[8]"/></span>
										<span title="Norfolk" class="county"><xsl:value-of disable-output-escaping="yes" select="county[9]"/></span>
										<span title="Bristol" class="county"><xsl:value-of disable-output-escaping="yes" select="county[10]"/></span>
										<span title="Plymouth" class="county"><xsl:value-of disable-output-escaping="yes" select="county[11]"/></span>
										<span title="Barnstable" class="county"><xsl:value-of disable-output-escaping="yes" select="county[12]"/></span>
										<span title="Dukes" class="county"><xsl:value-of disable-output-escaping="yes" select="county[13]"/></span>
										<span title="Nantucket" class="county"><xsl:value-of disable-output-escaping="yes" select="county[14]"/></span>									
									</td>
								</tr>
								<xsl:if test="nhesp_county">
								<tr>
									<td  nowrap="true"><a href="/admin/townmapper5/nhesptownrecord/?q={@pnid}">NHESP Records</a></td>
									<td>
										<xsl:for-each select="nhesp_county">
											<xsl:choose>
												<xsl:when test="@year">
													<span title="{@year}" class="county">+</span>
												</xsl:when>
												<xsl:otherwise>
													<span title="None" class="county">&#160;</span>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:for-each>
									</td>
								</tr>
								</xsl:if>
								<xsl:if test="generic_county">
								<tr>
									<td   nowrap="true" title=""><a href="/admin/survey/genericrecord/?q={@pnid}">Other/Generic Records</a></td>
									<td>
										<xsl:for-each select="generic_county">
											<xsl:choose>
												<xsl:when test="@year">
													<xsl:choose>
														<xsl:when test="@status">
															<span title="{@year}" class="county" style="color:white;background-color:black">del</span>
														</xsl:when>
														<xsl:when test="@native_status">
															<span title="{@year}: {@native_status}" class="county" style="background-color:yellow"><xsl:value-of select="@native_status"/></span>
														</xsl:when>
														<xsl:otherwise>
															<span title="{@year}" class="county">+</span>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:otherwise>
													<span title="None" class="county">&#160;</span>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:for-each>
									</td>
								</tr>
								</xsl:if>
<xsl:if test="$authorized and ./cnh_county">
<tr>
	<td nowrap="true" title=""><a href="/admin/townmapper5/cnhrecord/?q={@pnid}">CNH Portal Records</a></td>
	<td>
		<xsl:for-each select="cnh_county">
			<xsl:choose>
				<xsl:when test="@year">
							<span title="{@year}" class="county">+</span>
				</xsl:when>
				<xsl:otherwise>
					<span title="None" class="county">&#160;</span>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
	</td>
</tr>
</xsl:if>
								
								
								<xsl:if test="photo_county">
								<tr>
									<td nowrap="true" title="">Salicicola Photo Records</td>
									<td>
										<xsl:for-each select="photo_county">
											<xsl:choose>
												<xsl:when test="@phids">
													<xsl:choose>
														<xsl:when test="@phids = @planted">
															<span title="" class="county" style="background-color:yellow">c</span>
														</xsl:when>
														<xsl:when test="@native_status and string-length(@native_status)">
															<span title="" class="county" style="background-color:violet"><xsl:value-of select="@native_status"/></span>
														</xsl:when>
														<xsl:otherwise>
															<span title="" class="county"><a style="text-decoration:none" target="_blank" href="/photodb/gallery/simple/{../@pnid}/{@abbr}/">+</a></span> 
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:otherwise>
													<span title="None" class="county">&#160;</span>
												</xsl:otherwise>
											</xsl:choose>	
											<xsl:copy-of select="."/>
										</xsl:for-each>
									</td>
								</tr>
								</xsl:if>
<xsl:if test="annotation[not(@kind='photo')]">							
	<tr>
		<td nowrap="true" title=""><b>Annotations</b>:</td>
		<td> 
			<xsl:for-each select="annotation[not(@kind='photo')]">
				<b title="{@by}"><xsl:value-of select="@kind"/></b>:
				<xsl:copy-of select="note/*|note/text()"/>
				<xsl:if test="@url"> [<xsl:value-of select="@url"/>]</xsl:if>
				<xsl:if test="not(position() = last())"><br/></xsl:if>
			</xsl:for-each>
		</td>
	</tr>
</xsl:if>								
								</tbody>
						</table>							
					</div>		
					<!--
					<xsl:if test="prv_note">
						<div style="padding-left:2ex"><xsl:copy-of select="prv_note/text()|prv_note/*"/></div>
					</xsl:if>
					
					<xsl:if test="pub_note">
						<div style="padding-left:2ex"><b>Notes: </b> <xsl:copy-of select="pub_note/text()|pub_note/*" /> </div>
						
					</xsl:if>
					-->
				</div>	
	</xsl:template>
</xsl:stylesheet>
