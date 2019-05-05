<?xml version='1.0' encoding='ascii' ?>
<xsl:transform version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<!--xsl:output method='xml' media-type='application/xhtml+xml'/-->
	<xsl:output method='html' media-type='text/html'/>

	<xsl:template match='/part'>
		<!--DOCTYPE html-->
		<!--html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"-->
		<html lang="en">
			<head>
				<meta name='description' content='Benchmarks of various build tools'/>
				<meta name='keywords' content='build tool c++ gcc make scons waf python autotools automake libtool open source free software gnu linux gpl'/>
				<link rel='shortcut icon' href='http://psycle.sourceforge.net/favicon.ico' type='image/x-icon'/>
				<link rel='stylesheet' href='time.css' type='text/css' title='psycledelics'/>
				<!--style type='text/css' title='psycledelics'>
					@import url(time.css);
				</style-->
				<link rel='home' title='Home' href='http://retropaganda.info/~bohan/devel/wonderbuild'/>
				<link rel='author' title='Author' href='http://retropaganda.info/~bohan'/>
				<title><xsl:value-of select='@caption'/></title>
			</head>
			<body>
				<xsl:call-template name='caption-root'>
					<xsl:with-param name='location'>top</xsl:with-param>
				</xsl:call-template>
				<div class='body-root'>
					<div class='body'>
						<xsl:apply-templates select='text()|*[name()!="part"]'/>
					</div>
					<!--hr style='page-break-after: always'/-->
					<div class='part-root'>
						<div class='caption'>
							Table of content <!--of <xsl:apply-templates select='@caption'/>-->
						</div>
						<div class='index'>
							<xsl:apply-templates select='part' mode='index'/>
						</div>
						<!--div class='caption'>
							Table of Content--> <!--of <xsl:apply-templates select='@caption'/>-->
							<!--div class='part-body'-->
								<xsl:apply-templates select='part'/>
							<!--/div-->
						<!--/div-->
					</div>
				</div>
				<xsl:call-template name='caption-root'>
					<xsl:with-param name='location'>bottom</xsl:with-param>
				</xsl:call-template>
			</body>
		</html>
	</xsl:template>
	
	<xsl:template name='caption-root'>
		<xsl:param name='location'/>
		<xsl:param name='image'><xsl:value-of select='@image'/></xsl:param>
		<xsl:param name='alt'><xsl:value-of select='@alt'/></xsl:param>
		<div class='caption-root'>
			<table class='caption-root'>
				<tr>
					<td nowrap='true'>
						<a href='http://retropaganda.info/~bohan/devel/wonderbuild'>
							<img alt='{$alt}' border='0' align='left' width='64px' height='64px' src='{$image}'/>
						</a>
					</td>
					<td nowrap='true'>
						<xsl:choose>
							<xsl:when test='$location="top"'>
								<xsl:apply-templates select='@caption'/>
							</xsl:when>
							<xsl:when test='$location="bottom"'>
								<i style='font-family: URW Chancery L, cursive'><xsl:text>Fin</xsl:text></i>
							</xsl:when>
						</xsl:choose>
					</td>
				</tr>
			</table>
		</div>
	</xsl:template>

	<xsl:template match='part' mode='index'>
		<xsl:param name='level'><xsl:value-of select='position()'/></xsl:param>
		<xsl:param name='path'><xsl:value-of select='$level'/></xsl:param>
		<table border='0' cellspacing='0' cellpadding='0' class='index'>
			<tr>
				<td nowrap='true'>
					<a name='-{$path}'>
						<a href='#{$path}'>
							<xsl:value-of select='$path'/>
						</a>
						&#160;
					</a>
				</td>
				<td nowrap='true'>
					<a href='#{$path}' class='hidden'>
						<xsl:apply-templates select='@caption'/>
					</a>
				</td>
			</tr>
			<xsl:if test='part'>
				<tr>
					<td>
						&#160;
					</td>
					<td>
						<div class='part' style='margin-top: 0.25em; margin-bottom: 0.25em;'>
							<xsl:for-each select='part'>
								<xsl:apply-templates select='.' mode='index'>
									<xsl:with-param name='path'>
										<xsl:value-of select='$path'/>
										<xsl:text>.</xsl:text>
										<xsl:value-of select='position()'/>
									</xsl:with-param>
								</xsl:apply-templates>
							</xsl:for-each>
						</div>
					</td>
				</tr>
			</xsl:if>
		</table>
	</xsl:template>

	<xsl:template match='part'>
		<xsl:param name='level'><xsl:value-of select='position()'/></xsl:param>
		<xsl:param name='path'><xsl:value-of select='$level'/></xsl:param>
		<!--xsl:if test='$level=1'><hr style='page-break-after: always'/></xsl:if-->
		<a name='{$path}'/>
		<xsl:if test='"{@anchor}" != ""'>
			<a name='{@anchor}'/>
		</xsl:if>
		<div style='page-break-inside: avoid' class='caption'>
			<div nowrap='true'>
				<a href='#-{$path}'><xsl:value-of select='$path'/></a>
				<xsl:text>&#160;&#160;</xsl:text>
				<xsl:apply-templates select='@caption'/>
			</div>
		</div>
		<div class='part-body'>
			<div class='body'>
				<xsl:apply-templates select='text()|*[name()!="part"]'/>
			</div>
			<xsl:if test='part'>
				<xsl:for-each select='part'>
					<div class='part'>
						<xsl:apply-templates select='.'>
							<xsl:with-param name='path'><xsl:value-of select='$path'/>.<xsl:value-of select='position()'/></xsl:with-param>
							<xsl:with-param name='level' select='$level + 1'/>
						</xsl:apply-templates>
					</div>
				</xsl:for-each>
			</xsl:if>
		</div>
	</xsl:template>

	<xsl:template match='b|i|s|u|br|hr|ol|ul|li|pre|table|th|tr|td|div|span|p|code|em|script|object|param|embed'>
		<xsl:copy>
			<xsl:copy-of select='@*'/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>

	<xsl:template match='img'>
		<xsl:copy>
			<xsl:attribute name='style'>page-break-before: never</xsl:attribute>
			<xsl:copy-of select='@*'/>
		</xsl:copy>
	</xsl:template>

	<xsl:template match='a'>
		<xsl:copy>
			<xsl:copy-of select='@*'/>
			<xsl:choose>
				<xsl:when test='text()|node()'>
					<xsl:apply-templates/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select='@href'/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>

	<xsl:template match='iframe'>
		<xsl:copy>
			<xsl:copy-of select='@*'/>
		</xsl:copy>
	</xsl:template>

	<xsl:template match='bars'>
		<xsl:param name='scale'>
			<xsl:choose>
				<xsl:when test='@scale'><xsl:value-of select='@scale'/></xsl:when>
				<xsl:otherwise>1</xsl:otherwise>
			</xsl:choose>
		</xsl:param>
		<xsl:param name='unit'>
			<xsl:choose>
				<xsl:when test='@unit'><xsl:value-of select='@unit'/></xsl:when>
				<xsl:otherwise>s</xsl:otherwise>
			</xsl:choose>
		</xsl:param>
		<table class='bar'>
			<xsl:apply-templates>
				<xsl:with-param name='scale'>
					<xsl:value-of select='$scale'/>
				</xsl:with-param>
				<xsl:with-param name='unit'>
					<xsl:value-of select='$unit'/>
				</xsl:with-param>
			</xsl:apply-templates>
		</table>
	</xsl:template>
	
	<xsl:template match='bar-section'>
		<tr class='bar-section'>
			<td class='bar-section' colspan='7'>
				<xsl:apply-templates/>
			</td>
		</tr>
	</xsl:template>

	<xsl:template match='bar'>
		<xsl:param name='scale'/>
		<xsl:param name='unit'/>
		<tr>
			<td align='right'><xsl:value-of select='@name'/></td>
			<td>&#160;</td>
			<td align='right'><code><xsl:value-of select='@value'/><xsl:value-of select='$unit'/></code></td>
			<xsl:choose>
				<xsl:when test='@value * $scale > 10000'>
					<td>
						<div class='bar' style='width: 9500px'>
							&#160;
							<span class='bar-note'><xsl:apply-templates/></span>
						</div>
					</td>
					<td><span style='color: red'>//</span></td>
					<td><div class='bar' style='width: 50px'>&#160;</div></td>
				</xsl:when>
				<xsl:otherwise>
					<td colspan='3'>
						<div class='bar'>
							<xsl:attribute name='style'>width: <xsl:number value='@value * $scale'/>px</xsl:attribute>
							&#160;
							<span class='bar-note'><xsl:apply-templates/></span>
						</div>
					</td>
				</xsl:otherwise>
			</xsl:choose>
		</tr>
	</xsl:template>

</xsl:transform>
