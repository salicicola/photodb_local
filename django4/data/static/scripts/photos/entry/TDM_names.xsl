<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:param name="text" select="''"/>
	<xsl:template match="/">
		<select id="pnids" size="5" onchange="updateName(this)" onclick="updateName(this)" style="z-index:3;background-color:lightgreen">
			<option value="999999999/999999999">Unknown</option>
			<xsl:for-each select="/*/*[@status = 'valid' and contains(., $text)]">
				<xsl:variable name="content">
					<xsl:value-of select="latname"/>
					<xsl:if test="string-length(colname)"> (<xsl:value-of select="colname"/>)</xsl:if>
				</xsl:variable>
				<option value="{fileID}/{PNID}">
					<xsl:if test="position() = 1 and position() = last()">
						<xsl:attribute name="selected">true</xsl:attribute>
					</xsl:if>
					<xsl:value-of select="normalize-space($content)"/>
				</option>
			</xsl:for-each>
		</select>
	</xsl:template>
</xsl:stylesheet>
