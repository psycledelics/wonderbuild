<?xml version='1.0' encoding='ascii' ?>
<xsl:transform version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<!--xsl:output method='xml'/-->
	<xsl:output method='html'/>
	<!--xsl:output method='text'/-->

	<xsl:template match='/part'>
		<!--DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"-->
		<html>
			<head>
				<meta name='description' content='Benchmarks of various build tools'/>
				<meta name='keywords' content='build tool c++ gcc make scons waf python autotools automake libtool open source free software gnu linux gpl'/>
				<link rel='shortcut icon' href='http://psycle.sourceforge.net/favicon.ico' type='image/x-icon'/>
				<link rel='stylesheet' href='time.css' type='text/css' title='psycledelics'/>
				<!--style type='text/css' title='psycledelics'>
					@import url(time.css);
				</style-->
				<link rel='home' title='Home' href='http://retropaganda.info/~bohan/work/sf/psycle/branches/bohan/wonderbuild'/>
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
						<a href='http://retropaganda.info/~bohan/work/sf/psycle/branches/bohan/wonderbuild'>
							<img alt='{$alt}' border='0' align='left' src='{$image}'/>
						</a>
					</td>
					<td nowrap='true'>
						<xsl:text>&lt;</xsl:text>
						<xsl:choose>
							<xsl:when test='$location="top"'>
							</xsl:when>
							<xsl:when test='$location="bottom"'>
								<xsl:text>/</xsl:text>
							</xsl:when>
						</xsl:choose>
						<xsl:apply-templates select='@caption'/>&gt;
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

	<xsl:template match='b|i|s|u|br|hr|ol|ul|li|pre|table|th|tr|td|div|span|p|code|em|script|object|param|embeed'>
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

	<xsl:template match='bar'>
		<td>
			<div class='bar'>
				<xsl:attribute name='style'>width: <xsl:value-of select='@width'/>px</xsl:attribute>
				&#160;
			</div>
		</td>
	</xsl:template>

</xsl:transform>
