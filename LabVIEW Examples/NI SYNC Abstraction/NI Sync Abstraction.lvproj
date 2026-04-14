<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="14008000">
	<Item Name="My Computer" Type="My Computer">
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="Clock VIs" Type="Folder">
			<Item Name="Connect Clock Terminals.vi" Type="VI" URL="../Lib/Connect Clock Terminals.vi"/>
			<Item Name="Disconnect Clock Terminals-Array.vi" Type="VI" URL="../Lib/Disconnect Clock Terminals-Array.vi"/>
			<Item Name="Disconnect Clock Terminals.vi" Type="VI" URL="../Lib/Disconnect Clock Terminals.vi"/>
			<Item Name="Connect Clock Terminals-Array.vi" Type="VI" URL="../Lib/Connect Clock Terminals-Array.vi"/>
		</Item>
		<Item Name="Controls" Type="Folder">
			<Item Name="Clock Routing.ctl" Type="VI" URL="../Lib/Clock Routing.ctl"/>
			<Item Name="Trigger Routing.ctl" Type="VI" URL="../Lib/Trigger Routing.ctl"/>
		</Item>
		<Item Name="Trigger VIs" Type="Folder">
			<Item Name="Connect Trigger Terminals-Array.vi" Type="VI" URL="../Lib/Connect Trigger Terminals-Array.vi"/>
			<Item Name="Connect Trigger Terminals.vi" Type="VI" URL="../Lib/Connect Trigger Terminals.vi"/>
			<Item Name="Disonnect Trigger Terminals-Array.vi" Type="VI" URL="../Lib/Disonnect Trigger Terminals-Array.vi"/>
			<Item Name="Disonnect Trigger Terminals.vi" Type="VI" URL="../Lib/Disonnect Trigger Terminals.vi"/>
		</Item>
		<Item Name="Poly" Type="Folder">
			<Item Name="Trigger_Poly.vi" Type="VI" URL="../Lib/Trigger_Poly.vi"/>
			<Item Name="Clock_Poly.vi" Type="VI" URL="../Lib/Clock_Poly.vi"/>
		</Item>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="instr.lib" Type="Folder">
				<Item Name="niSync Connect Clock Terminals.vi" Type="VI" URL="/&lt;instrlib&gt;/niSync/niSync.llb/niSync Connect Clock Terminals.vi"/>
				<Item Name="niSync Connect Trigger Terminals.vi" Type="VI" URL="/&lt;instrlib&gt;/niSync/niSync.llb/niSync Connect Trigger Terminals.vi"/>
				<Item Name="niSync Disconnect Clock Terminals.vi" Type="VI" URL="/&lt;instrlib&gt;/niSync/niSync.llb/niSync Disconnect Clock Terminals.vi"/>
				<Item Name="niSync Disconnect Trigger Terminals.vi" Type="VI" URL="/&lt;instrlib&gt;/niSync/niSync.llb/niSync Disconnect Trigger Terminals.vi"/>
				<Item Name="niSync IVI Error Converter.vi" Type="VI" URL="/&lt;instrlib&gt;/niSync/niSync.llb/niSync IVI Error Converter.vi"/>
			</Item>
			<Item Name="vi.lib" Type="Folder">
				<Item Name="IVI Error Message Builder.vi" Type="VI" URL="/&lt;vilib&gt;/errclust.llb/IVI Error Message Builder.vi"/>
			</Item>
			<Item Name="niSync.dll" Type="Document" URL="niSync.dll">
				<Property Name="NI.PreserveRelativePath" Type="Bool">true</Property>
			</Item>
		</Item>
		<Item Name="Build Specifications" Type="Build"/>
	</Item>
</Project>
