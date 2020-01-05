<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="plugins">

<html>
<head>
<title>Plugins Géo2France</title>

<style>
body  {
  font-family:Verdana, Arial, Helvetica, sans-serif;
  width: 45em;
}
a{
  color:black;
}
div.head {
  background-color:#114496;
  border-bottom-width:0;
  color:#fff;
  display:block;
  font-size:100%;
  font-weight:bold;
  margin:0;
  padding:0.3em 1em;
}
div.plugin {
  _background-color:#ddfb63;
  border: solid 1px #114496;
  clear:both;
  display:block;
  padding:0 0 0.5em;
  margin:1em;
}
/*div.description{
  display: block;
  float:none;
  margin:0;
  text-align: left;
  padding:0.2em 0.5em 0.4em;
  color: black;
  font-size:85%;
  font-weight:normal;
  font-style: italic;
}
div.about{
  display: block;
  float:none;
  margin:0;
  text-align: left;
  padding:0.2em 0.5em 0.4em;
  color: black;
  font-size:85%;
  font-weight:normal;
 }*/
div.tag{
  padding:0 0 0 1em;
  font-size:85%;
  font-weight:normal;
}
div.download, div.author, div.branch{
  font-size: 80%;
  padding: 0em 0em 0em 1em;
 }
</style>

</head>
<body>
<img src="geo2france.png" width="20%"/>
<h2>Plugins pour QGIS 2</h2>
<table>
<tr>

<td class="body_panel">
<xsl:for-each select="/plugins/pyqgis_plugin">
<xsl:sort select="@name"/>
<div class="plugin">
<div class="head">
<xsl:value-of select="@name" /> : <xsl:value-of select="@version" />
</div>
<!--div class="description">
Description<xsl:text>&#160;</xsl:text>: <xsl:value-of select="description" />
</div>
<div class="about">
<xsl:value-of select="about" />
</div-->
<div class="tag">
<xsl:value-of select="description" /><br/>
<xsl:value-of select="about" /><br/><br/>
<xsl:value-of select="tags" />
</div>
<div class="tag">
Téléchargement<xsl:text>&#160;</xsl:text>:
<xsl:element name="a">
 <xsl:attribute name="href">
  <xsl:value-of select="download_url" />
 </xsl:attribute>
 <xsl:value-of select="file_name" />
</xsl:element>
</div>
<div class="tag">
Auteur<xsl:text>&#160;</xsl:text>: <xsl:value-of select="author_name" />
</div>
<div class="tag">
Version<xsl:text>&#160;</xsl:text>: <xsl:value-of select="version" />
</div>
<div class="tag">
Experimental<xsl:text>&#160;</xsl:text>: <xsl:value-of select="experimental" />
</div>
<div class="tag">
Obsolète<xsl:text>&#160;</xsl:text>: <xsl:value-of select="deprecated" />
</div>
<div class="tag">
Version minimum de QGIS<xsl:text>&#160;</xsl:text>: <xsl:value-of select="qgis_minimum_version" />
</div>
<div class="tag">
Version maximum de QGIS<xsl:text>&#160;</xsl:text>: <xsl:value-of select="qgis_maximum_version" />
</div>


</div>
</xsl:for-each>
</td>
</tr>
</table>
</body>
</html>

</xsl:template>

</xsl:stylesheet>
